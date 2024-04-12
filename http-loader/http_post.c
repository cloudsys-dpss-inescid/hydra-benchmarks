#include <limits.h>
#include <math.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <netdb.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>


#define BUFFER_SIZE 1024    // Default size used to initialize arrays for sending and receiving messages with the server
#define HTTP_HEADER 74      // This is the size of the header without the length digit
#define DEBUG_MODE false    // If set to true, it will print debug information, such as the content of the messages from the server


char *host;
int port;
char *payload_path;
int threads_number;
int workload;
char global_payload[BUFFER_SIZE]; 
char request[BUFFER_SIZE];
char *results_directory;
size_t global_payload_size; 
char request_template[] = "POST / HTTP/1.1\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %lu\r\n\r\n%s";

typedef struct {
    int thread_id;
    int socket_id; 
} ThreadParams;


int extract_content_length(const char *response) {
    // Looking for the content  keyword "Content-Length"
    const char *content_length_start = strstr(response, "Content-length: ");
    if (content_length_start != NULL) {
        content_length_start += strlen("Content-length: ");

        // Extract the value of "Content-Length" as a string
        char *endptr;
        int content_length = strtol(content_length_start, &endptr, 10);
        if (endptr != content_length_start && *endptr == '\r') {
            return content_length;
        }
    }

    // If didn't find the "Content-Length" field or the value is not valid, return -1
    return -1;
}

int character_counter(int value) {
    // If the value is 0, we need 1 character
    if (value == 0) {
        return 1;
    }
    // If the value is negative, add 1 for the '-'
    int size= (value < 0) ? 1 : 0;
    // Calculate the number of digits in the absolute value of the number
    size += (int)log10(abs(value)) + 1;
    return size;
}

void magic_socket(int local_socket) {
    
    int flag = 1;
    setsockopt(local_socket, IPPROTO_TCP, TCP_NODELAY, (char *)&flag, sizeof(int));
    setsockopt(local_socket, IPPROTO_TCP, TCP_QUICKACK, (char *) &flag, sizeof(int));
}

// Function to establish connection to the server
int connect_to_server(const char* host, int port) {
    // Set up address structure
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);

    struct addrinfo hints, *res;
    int status;

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET; // AF_INET para IPv4, AF_INET6 para IPv6, ou AF_UNSPEC para ambos
    hints.ai_socktype = SOCK_STREAM;

    if ((status = getaddrinfo(host, NULL, &hints, &res)) != 0) {
        fprintf(stderr, "Error getting host info: %s\n", gai_strerror(status));
       return -1; 
    }

    // The res structure contains a list of addresses; you can simply use the first one
    server_addr.sin_addr = ((struct sockaddr_in*)res->ai_addr)->sin_addr;
    server_addr.sin_port = htons(port); 
    
    // Create and connect sockets
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Error creating socket");
        return -1;
    }
    
    // Connect to the server
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Error connecting to server");
        close(sockfd);
        return -1;
    }

    return sockfd;
}

void *run_request(void *arg) {

    ThreadParams *params = (ThreadParams *)arg;
    int thread_id = params->thread_id; 
    int sockfd = params->socket_id;

    // Define reference time: January 1, 2020. This also done in the server side to synchronize with the CPU usage.
    struct tm ref = {0};
    ref.tm_year = 120; // Year since 1900
    ref.tm_mday = 1;   // Day of the month
    time_t ref_time_t = mktime(&ref);
    long nano_ref = ref_time_t * 1000000000; // this is in nanoseconds

    // Dynamic allocation based on workload
    long *elapsed_time = (long *)malloc(workload * sizeof(long));
    long *start_timestamp = (long *)malloc(workload * sizeof(long));
    
    // Check if allocation was successful
    if (!elapsed_time || !start_timestamp) {
        perror("Memory allocation error");
        free(elapsed_time); // Free memory if one of the allocations fail
        free(start_timestamp);
        pthread_exit(NULL);
    }

    // Buffer to store received data
    char response[BUFFER_SIZE];
    magic_socket(sockfd);
    
    // Execute the request
    for (int i = 0; i < workload; i++) {

        struct timespec start, end;        
        // Measure start time
        clock_gettime(CLOCK_REALTIME, &start);

         // Send request
        if (send(sockfd, request, strlen(request), 0) < 0) {
            perror("Error sending request");
            close(sockfd);
            pthread_exit(NULL);
        }

        // Receive HTTP response
        magic_socket(sockfd);

        ssize_t bytes_recv = 0;
        ssize_t total_bytes_recv = 0;
        int content_length = 0;
        while ( (bytes_recv = recv(sockfd, &response[total_bytes_recv], BUFFER_SIZE - 1, 0) ) > 0){        
            
            total_bytes_recv += bytes_recv;
            content_length = extract_content_length(response);
            if(content_length<0){
                continue;
            }

            int digit_length = character_counter(content_length);        
            if(total_bytes_recv == content_length + HTTP_HEADER + digit_length){
                break;
            }

            if(total_bytes_recv > content_length + HTTP_HEADER + digit_length){ //This should not happen, if it does, it mean somethin in this math is wrong
                fprintf(stderr, "The client received more bytes than it should have; something is wrong with the request processing.\n" );
                response[total_bytes_recv] = '\0';
                printf("Server response (received %ld bytes and expected %d bytes, Thread %d):\n%s\n", total_bytes_recv, ( content_length + HTTP_HEADER + character_counter(content_length)), thread_id, response);                     
                break;
            }

        }

        if(DEBUG_MODE){
            response[total_bytes_recv] = '\0';
            printf("Server response (received %ld bytes and expected %d bytes, Thread %d):\n%s\n", total_bytes_recv, ( content_length + HTTP_HEADER + character_counter(content_length)), thread_id, response);           
        }

        if (bytes_recv < 0) {
            perror("Error receiving server response");
            close(sockfd);
            pthread_exit(NULL);
        } else if (bytes_recv == 0) {
            fprintf(stderr, "Connection closed by server, workload: %d, threadID: %d\n", i, thread_id );
            close(sockfd);
            pthread_exit(NULL);
        }
        
        // Measure end time
        clock_gettime(CLOCK_REALTIME, &end);

        // Calculate elapsed time in nanoseconds
        elapsed_time[i] = (end.tv_sec - start.tv_sec) * 1000000000 + (end.tv_nsec - start.tv_nsec); 
        long nano_start = start.tv_sec * 1000000000 + start.tv_nsec;
        start_timestamp[i] = nano_start - nano_ref;

    }

    // Close socket
    close(sockfd);
    // Write latencies to a file
    char filename[PATH_MAX]; 
    sprintf(filename, "%s/latency_thread%d.log", results_directory, thread_id);

    FILE *latency_file = fopen(filename, "w");
    if (latency_file == NULL) {
        perror("Error opening latency file");
        pthread_exit(NULL);
    }

    fprintf(latency_file, "Timestamp before sending request (ms), elapsed time from sending to receiving the response (ms)\n");
    for (int i = 0; i < workload; i++) {
        fprintf(latency_file, "%f,%f\n", (start_timestamp[i] / 1000000.0),  (elapsed_time[i] / 1000000.0) );
    }

    free(elapsed_time);
    free(start_timestamp);
    fclose(latency_file);
    if(DEBUG_MODE){
        printf("-Done: threadID: %d\n", thread_id );
    }

    pthread_exit(NULL);
}

// To make this work I had to change a line in SubstrateVMProxy.java (In Argo repository), otherwise I will receive the error "queue full", I have changed the line : this.queue = new ArrayBlockingQueue<>(2048);
// Usage example:  make clean && make && ./http_post 10.15.0.24 8081 payload.post 2 100  /home/claudiocorreia/remoteClient/http-loader/results/
int main(int argc, char *argv[]) {

    if (argc != 7) {
        fprintf(stderr, "Usage: %s <host> <port> <payload_file> <#threads> <workload> <results_directory>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    // Assign values to global variables
    host = argv[1];
    port = atoi(argv[2]);
    payload_path = argv[3];
    threads_number = atoi(argv[4]);
    workload = atoi(argv[5]);
    results_directory = argv[6];
    struct timespec global_start, global_end;
    
    // Open and read the content of the payload file once
    FILE *file = fopen(payload_path, "r");
    if (file == NULL) {
        perror("Error opening payload file");
        exit(EXIT_FAILURE);
    }
    global_payload_size = fread(global_payload, 1, BUFFER_SIZE, file);
    fclose(file);
    snprintf(request, BUFFER_SIZE, request_template, host, global_payload_size, global_payload);

    printf(" Running with workload: %d\n", threads_number);
    pthread_t threads[threads_number];
    ThreadParams *params_array = malloc(threads_number * sizeof(ThreadParams));
    if (params_array == NULL) {
        perror("Error allocating memory for thread parameters");
        exit(EXIT_FAILURE);
    }

    for (int i = 0; i < threads_number; i++) {
        params_array[i].thread_id = i;
        params_array[i].socket_id = connect_to_server(host, port);
    }

    printf("\nStrating threads\n");            
    clock_gettime(CLOCK_MONOTONIC, &global_start);    
    for (int i = 0; i < threads_number; i++) {
        if (pthread_create(&threads[i], NULL, run_request, (void *)&params_array[i]) != 0) {
            perror("Error creating thread");
            exit(EXIT_FAILURE);
        }
    }

    for (int i = 0; i < threads_number; i++) {
        if (pthread_join(threads[i], NULL) != 0) {
            perror("Error waiting for thread");
            exit(EXIT_FAILURE);
        }
    }

    // Measure end time
    clock_gettime(CLOCK_MONOTONIC, &global_end);

    // Calculate elapsed time in milliseconds
    double experiment_duration = (global_end.tv_sec - global_start.tv_sec) * 1000.0 + (global_end.tv_nsec - global_start.tv_nsec) / 1000000.0;
    
    printf("Experiment finished in %f ms, with %d threads, and each thread made %d requests/worload \n", experiment_duration, threads_number, workload);

    free(params_array);
 
    return 0;
}