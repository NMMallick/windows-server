#pragma once

#include <string>
#include <vector>
#include <map>

#include <stdio.h>
#include <stdlib.h>

#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#include "TaskPool.hh"

#pragma comment (lib, "Ws2_32.lib")
#define DEFAULT_BUFLEN 4096

struct client_
{
	SOCKET s = NULL;
	int buflen = DEFAULT_BUFLEN; 
	char recvbuf[DEFAULT_BUFLEN];
	char* sendbuf;
	bool busy;
	bool isPub;
	std::string topic;
};

class Server
{
private:
	WSADATA wsaData;
	SOCKET ListenSocket;

	std::vector<client_> client_sockets_;
	std::map<std::string, std::pair<uint32_t, uint16_t>> mapped_topics_;

	std::mutex socket_mutex_;

	TaskPool server_threads_;

	struct addrinfo *result = NULL;
	struct addrinfo hints; 

	bool done_;

public:
	Server() = delete;
	Server(const std::string &);
	~Server()
	{
		ShutDown();
	}

	void AcceptConnections();
	void CheckClients();
	void ShutDown();
	
};

Server::Server(const std::string &PORT_ADDR = "4000")
	: done_(false)
{
	printf("initializing socket with port %s\n", PORT_ADDR.c_str());

	// Initialize Winsock
	auto iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (iResult != 0)
	{
		printf("WSAStartup failed with error: %d\n", iResult);
		exit(1);
	}
	
	ZeroMemory(&hints, sizeof(hints));
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = IPPROTO_TCP;
	hints.ai_flags = AI_PASSIVE;
	
	std::string HOST = "0.0.0.0";

	// Resolve the server address and port
	iResult = getaddrinfo(HOST.c_str(), PORT_ADDR.c_str(), &hints, &result);
	if (iResult != 0)
	{
		printf("getaddrinfo failed with error: %d\n", iResult);
		WSACleanup();
		exit(1);
	}

	// Create a socket for the server to listen for client connections.
	ListenSocket = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
	if (ListenSocket == INVALID_SOCKET)
	{
		printf("socket failed with error: %ld\n", WSAGetLastError());
		freeaddrinfo(result);
		WSACleanup();
		exit(1);
	}

	// Setup the TCP listening socket
	iResult = bind(ListenSocket, result->ai_addr, (int)result->ai_addrlen);
	if (iResult == SOCKET_ERROR)
	{
		printf("bind failed with error: %d\n", WSAGetLastError());
		freeaddrinfo(result);
		closesocket(ListenSocket);
		WSACleanup();
		exit(1);
	}

	freeaddrinfo(result);

	server_threads_.start();
	printf("ready to accept client connections\n");
}

void Server::AcceptConnections()
{
	server_threads_.launch([&]() {
		while (!done_)
		{
			client_ c;
			printf("waiting for connections...\n");
			auto iResult = listen(this->ListenSocket, SOMAXCONN);
			if (iResult == SOCKET_ERROR)
			{
				printf("listen failed with error: %d\n", WSAGetLastError());
				closesocket(this->ListenSocket);
				WSACleanup();
				exit(1);
			}

			c.s = accept(this->ListenSocket, NULL, NULL);
			if (c.s == INVALID_SOCKET)
			{
				printf("accept failed with error: %d\n", WSAGetLastError());
				closesocket(this->ListenSocket);
				WSACleanup();
				exit(1);
			}

			//this->client_sockets_.push_back(c);
			c.busy = false; 
			std::unique_lock<std::mutex> lock(socket_mutex_);
			client_sockets_.push_back(c);

			printf("accepted client (id=%d)\n", this->client_sockets_.size()-1);
		}
		 
		closesocket(this->ListenSocket);
		return;
	});
}

void Server::CheckClients()
{
	unsigned long ul = 1;

	while (!done_)
	{
		std::unique_lock<std::mutex> lock(socket_mutex_);
		for (size_t i = 0; i < client_sockets_.size(); i++)
		{
			if (client_sockets_[i].busy)
				continue;


			ioctlsocket(client_sockets_[i].s, FIONBIO, &ul);
			auto iResult = recv(client_sockets_[i].s, client_sockets_[i].recvbuf, DEFAULT_BUFLEN, 0);
			
			if (iResult > 0) // Got a message 
			{
				// Record the byte size of data that's in the queue
				client_sockets_[i].busy = true;
				client_sockets_[i].buflen = iResult;

				// Have a thread deal with recieving that data 
				server_threads_.launch([&, i]() {
						std::unique_lock<std::mutex> lock(socket_mutex_);
				
						printf("Bytes received from client(%d) : %d\n", i, client_sockets_[i].buflen);
						
						// Register subscriber
						if (client_sockets_[i].recvbuf[0] == 0x01)
						{
							uint8_t topic_len = client_sockets_[i].recvbuf[1]; 
							client_sockets_[i].isPub = false; 

							// Extract topic from the buffer
							std::string topic;
							for (size_t k = 2; k < topic_len+2; k++)
								topic.push_back(client_sockets_[i].recvbuf[k]);
							
							printf("Node requesting subscription to topic (%s)\n", topic.c_str());
							client_sockets_[i].topic = topic;

							// Send URI info to the client  
							char pub_uri[6];

							if (mapped_topics_.count(topic)) // If there exists a publisher 
							{
								// Port Number
								pub_uri[5] = mapped_topics_[topic].second & 0xff; 
								pub_uri[4] = (mapped_topics_[topic].second >> 8) & 0xff; 

								// Host
								pub_uri[3] = mapped_topics_[topic].first & 0xff; 
								pub_uri[2] = (mapped_topics_[topic].first >> 8) & 0xff;
								pub_uri[1] = (mapped_topics_[topic].first >> 16) & 0xff;
								pub_uri[0] = (mapped_topics_[topic].first >> 24) & 0xff;							
							}
							else // Notify no active publisher 
							{
								for (size_t i = 0; i < 6; i++)
								{
									pub_uri[i] = 0x00; 
								}
							}

							send(client_sockets_[i].s, pub_uri, 6, 0);
							
						}
						
						// Register Publisher
						if (client_sockets_[i].recvbuf[0] == 0x00)
						{
							printf("Node is publishing with a host name of:\t");
							uint32_t hostname = 0;
							char pub_uri[6];

							for (size_t k = 1; k <= 4; ++k)
							{
								if (k != 4) printf("%u.", client_sockets_[i].recvbuf[k] & 0xff);
								else printf("%u", client_sockets_[i].recvbuf[k] & 0xff);
								pub_uri[k - 1] = client_sockets_[i].recvbuf[k] & 0xff;
								hostname = (hostname << 8) | (client_sockets_[i].recvbuf[k] & 0xff);
							}

							pub_uri[4] = (client_sockets_[i].recvbuf[5] & 0xff);
							pub_uri[5] = (client_sockets_[i].recvbuf[6] & 0xff);

							// Debugging
							printf("\n");
							uint16_t port_num = ((pub_uri[4] & 0xff) << 8) | (pub_uri[5] & 0xff);
							printf("At port number: %d\n", port_num);
							printf("byte 1: %u\nbyte 2: %u\n", pub_uri[4] & 0xff, pub_uri[5] & 0xff);



							uint8_t topic_len = client_sockets_[i].recvbuf[7];
							std::string topic;

							for (size_t k = 8; k < topic_len + 8; k++)
								topic.push_back(client_sockets_[i].recvbuf[k]);

							// Register the route 
							mapped_topics_[topic] = std::make_pair(hostname, port_num);

							// Register as a publisher and save its topic 
							client_sockets_[i].isPub = true;
							client_sockets_[i].topic = topic;

							printf("Topic: %s\n", topic.c_str());


							// TODO send the URI data to subscribers 
							for (auto sock : client_sockets_)
							{
								if (sock.isPub)
									continue;

								/*if (sock.busy)
									continue;*/

								if (sock.topic == topic)
								{
									// Waiting for socket to become free
									while (sock.busy);
									printf("Sending data to the client\n");
									send(sock.s, pub_uri, 6, 0);
								}
							}
						}

						client_sockets_[i].busy = false; 
						return;
					});
				
				continue;
			}
			else if (iResult == 0)
			{

				// Adjust the routing for new subscribers 
				if (client_sockets_[i].isPub)
				{
					mapped_topics_[client_sockets_[i].topic].first = 0x00; 
					mapped_topics_[client_sockets_[i].topic].second = 0x00;
				}
				
				printf("closing connection\n");
				closesocket(client_sockets_[i].s);
				client_sockets_.erase(client_sockets_.begin() + i);
				continue;
			}

			if (iResult < 0 && WSAGetLastError() == WSAEWOULDBLOCK)
				continue;
			else
			{
				printf("recv failed with error: %u\n", WSAGetLastError());
				closesocket(client_sockets_[i].s);
				client_sockets_.erase(client_sockets_.begin() + i);
			}
		}
	}

}

void Server::ShutDown()
{

	this->done_ = true;
	server_threads_.stop();

	printf("closing socket connections\n");
	for (size_t i = 0; i < client_sockets_.size(); i++)
		closesocket(client_sockets_[i].s);
	
	client_sockets_.clear();

	printf("shutting down server connections\n");
	closesocket(ListenSocket);

	WSACleanup();
}