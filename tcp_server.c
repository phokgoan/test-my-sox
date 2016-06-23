/*
	C socket server example
*/
 
#include <stdio.h>
#include <string.h>	//strlen
#include <sys/socket.h>
#include <arpa/inet.h> //inet_addr
#include <unistd.h>	//write
#include <time.h>
#include <signal.h>

#include "mongoc.h"

static volatile int keep_running = 1;
static int socket_desc;

void int_handler(int dummy) {
	
	char  c;

	signal(dummy, SIG_IGN);
	printf("\n\nOUCH, did you hit Ctrl-C?\nDo you really want to quit? [y/n] ");
	c = getchar();
	if (c == 'y' || c == 'Y') {
		keep_running = 0;
		int a = close(socket_desc);
		printf("The shutdown result: %d\n", a);
		exit(0);
	} else {
		signal(SIGINT, int_handler);
	}
}

int main(int argc , char *argv[])
{
	signal(SIGINT, int_handler);
	while (keep_running) {
		char *client_ip;
		int client_sock, c, read_size;
		struct sockaddr_in server, client;
		char client_message[2000];

		struct timeval current;

		const int enable = 1;

		mongoc_client_t	  *mongo_client;
		mongoc_collection_t *collection;
		bson_error_t error;
		bson_oid_t oid;

		mongoc_init ();
		mongo_client = mongoc_client_new ("mongodb://localhost:27017");
		collection = mongoc_client_get_collection (mongo_client, "socket_logs", "tcp_server");

		//Create socket
		socket_desc = socket(AF_INET , SOCK_STREAM , 0);
		if (socket_desc == -1)
		{
			printf("Could not create socket");
		}
		puts("Socket created");

		//Prepare the sockaddr_in structure
		server.sin_family = AF_INET;
		server.sin_addr.s_addr = inet_addr(SERVICE_IP);
		server.sin_port = htons(SERVICE_TCP_PORT);

		printf("Currently serving on %s:%d\n", SERVICE_IP, SERVICE_TCP_PORT);

		setsockopt(socket_desc, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int));

		//Bind
		if( bind(socket_desc,(struct sockaddr *)&server , sizeof(server)) < 0)
		{
			//print the error message
			perror("bind failed. Error");
			return 1;
		}
		puts("bind done");

		//printf("The process reaches %s:%d, in %s\n", __FILE__, __LINE__, __func__);

		while(1) {
			//Listen
			listen(socket_desc , 3);

			//Accept and incoming connection
			puts("Waiting for incoming connections...");
			c = sizeof(struct sockaddr_in);

			//accept connection from an incoming client
			client_sock = accept(socket_desc, (struct sockaddr *)&client, (socklen_t*)&c);

			client_ip = inet_ntoa(client.sin_addr);

			//printf("The process reaches %s:%d, in %s\n", __FILE__, __LINE__, __func__);

			if (client_sock < 0)
			{
				perror("accept failed");
				return 1;
			}
			puts("Connection accepted");

			//Receive a message from client
			while( (read_size = recv(client_sock , client_message , 2000 , 0)) > 0 )
			{
				//Send the message back to client
				uint8_t message[2000];
				bson_t *doc;

				//printf("The process reaches %s:%d, in %s\n", __FILE__, __LINE__, __func__);
				
				memcpy(message, client_message, read_size);

				//printf("The process reaches %s:%d, in %s\n", __FILE__, __LINE__, __func__);

				//printf("%s\r\n", client_message);
				//write(1 , client_message , read_size);

				gettimeofday(&current, NULL);
	
				doc = bson_new();
				bson_oid_init (&oid, NULL);
				BSON_APPEND_OID (doc, "_id", &oid);
				BSON_APPEND_UTF8 (doc, "ip", client_ip);
				BSON_APPEND_BINARY(doc, "message", BSON_SUBTYPE_BINARY, message, read_size);
				BSON_APPEND_DATE_TIME(doc, "date", (int64_t) (current.tv_sec*1000) + (int64_t) (current.tv_usec/1000));

				if (!mongoc_collection_insert (collection, MONGOC_INSERT_NONE, doc, NULL, &error)) {
					fprintf (stderr, "%s\n", error.message);
					printf("%s\n", error.message);
				}

				bson_destroy (doc);
			}

			if(read_size == 0)
			{
				puts("Client disconnected");
				fflush(stdout);
			}
			else if(read_size == -1)
			{
				perror("recv failed");
			}
		}

		mongoc_collection_destroy (collection);
		mongoc_client_destroy (mongo_client);
		mongoc_cleanup ();
	}
	return 0;
}
