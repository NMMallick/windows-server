#undef UNICODE

#define WIN32_LEAN_AND_MEAN

#include "Server.hh"

#define DEFAULT_BUFLEN 512
#define DEFAULT_PORT "27015"

int __cdecl main(void)
{
	Server server(DEFAULT_PORT);
	server.AcceptConnections(); // Checks continously for connection in 1 thread
	server.CheckClients(); // Checks each "established" connection for incoming data and forwards it to the appropriate client

	return 0;
}