#pragma once

#include <string>
#include <vector>
#include <stdio.h>
#include <stdlib.h>

#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#include "TaskPool.hh"

#pragma comment (lib, "Ws2_32.lib")
#define DEFAULT_BUFLEN 512

struct client_
{
	SOCKET s;
	int buflen = DEFAULT_BUFLEN; 
	char buf[DEFAULT_BUFLEN];
};

class Server
{
private:
	WSADATA wsaData;
	SOCKET ListenSocket;

	std::vector<client_> client_sockets_;
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

	// Resolve the server address and port
	iResult = getaddrinfo(NULL, PORT_ADDR.c_str(), &hints, &result);
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
			ioctlsocket(client_sockets_[i].s, FIONBIO, &ul);
			auto iResult = recv(client_sockets_[i].s, client_sockets_[i].buf, DEFAULT_BUFLEN, 0);
		
			if (iResult > 0) // Got a message 
			{
				// Record the byte size of data that's in the queue
				client_sockets_[i].buflen = iResult;

				// Have a thread deal with recieving that data 
				server_threads_.launch([&, i]() {
					std::unique_lock<std::mutex> lock(socket_mutex_);
				
					// Handle message

					// DEBUG
					printf("Bytes received from client(%d) : %d\n", i, client_sockets_[i].buflen);				
					printf("(CHAR OUTPUT)\t");
					for (size_t j = 0; j < client_sockets_[i].buflen; j++)
					{
						printf("%c", client_sockets_[i].buf[j]);
					}
					printf("\n");

					});
				continue;
			}
			else if (iResult == 0)
			{
				printf("closing connection\n");
				closesocket(client_sockets_[i].s);
				client_sockets_.erase(client_sockets_.begin() + i);
				continue;
			}

			if (iResult < 0 && WSAGetLastError() == WSAEWOULDBLOCK)
				continue;
			else
			{
				printf("recv failed with error: %d\n", WSAGetLastError());
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