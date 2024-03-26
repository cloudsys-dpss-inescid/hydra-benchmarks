#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <pthread.h>
#include <time.h>
#include <sys/stat.h>
#include <netinet/tcp.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h> 
#include <limits.h>

#define BUFFER_SIZE 1024
#define HTTP_HEADER 74 // it is the size of the header wihtou the length digit
#define MAX_REQUESTS 10000
#define DEBUG_MODE false


char *host;
int port;
char *arquivo_payload;
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

int character_counter(int valor) {
    // If the value is 0, we need 1 character
    if (valor == 0) {
        return 1;
    }
    // If the value is negative, add 1 for the '-'
    int tamanho = (valor < 0) ? 1 : 0;
    // Calculate the number of digits in the absolute value of the number
    tamanho += (int)log10(abs(valor)) + 1;
    return tamanho;
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
        pthread_exit(NULL);
    }

    // The res structure contains a list of addresses; you can simply use the first one
    server_addr.sin_addr = ((struct sockaddr_in*)res->ai_addr)->sin_addr;
    server_addr.sin_port = htons(port); // Don't forget to assign the port

    
    
    // Create and connect sockets
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Error creating socket");
        pthread_exit(NULL);
    }

    
    // Connect to the server
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Error connecting to server");
        close(sockfd);
        pthread_exit(NULL);
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
    double ms_ref = ref_time_t * 1000.0;

    // Dynamic allocation based on workload
    double *elapsed_time = (double *)malloc(workload * sizeof(double));
    double *start_timestamp = (double *)malloc(workload * sizeof(double));
    
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

        // Read HTTP response once
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
            if(total_bytes_recv >= content_length + HTTP_HEADER + digit_length){ //I should duble check if it is =>
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
            sockfd = connect_to_server(host, port); // Reconnect
            magic_socket(sockfd);

            i--; // Retry the same request
        }
        






        // Measure end time
        clock_gettime(CLOCK_REALTIME, &end);

        // Calculate elapsed time in milliseconds
        elapsed_time[i] = (end.tv_sec - start.tv_sec) * 1000.0 + (end.tv_nsec - start.tv_nsec) / 1000000.0; 
        double ms_start= start.tv_sec * 1000.0 + start.tv_nsec / 1000000.0;
        start_timestamp[i] = ms_start - ms_ref;

    }

    // Close socket
    close(sockfd);

    // Write latencies to a file
    char filename[PATH_MAX]; 

    sprintf(filename, "%s/latencias_thread%d.log", results_directory, thread_id);

    FILE *latency_file = fopen(filename, "w");
    if (latency_file == NULL) {
        perror("Error opening latency file");
        pthread_exit(NULL);
    }

    fprintf(latency_file, "Timestamp before sending request (ms), elapsed time from sending to receiving the response (ms)\n");
    for (int i = 0; i < workload; i++) {
        fprintf(latency_file, "%f,%f\n",start_timestamp[i],  elapsed_time[i]);
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
// Usage example:  make clean && make && ./http_post 146.193.41.25 8080 payload.post 256 8192  /home/ccorreia/graal_test/tmp/

int main(int argc, char *argv[]) {
    if (argc != 7) {
        fprintf(stderr, "Usage: %s <host> <port> <payload_file> <#threads> <workload> <results_directory>\n", argv[0]);
        exit(EXIT_FAILURE);
    }


    // Assign values to global variables
    host = argv[1];
    port = atoi(argv[2]);
    arquivo_payload = argv[3];
    threads_number = atoi(argv[4]);
    workload = atoi(argv[5]);
    results_directory = argv[6];
    struct timespec global_start, global_end;


    
    // Open and read the content of the payload file once
    FILE *file = fopen(argv[3], "r");
    if (file == NULL) {
        perror("Error opening payload file");
        exit(EXIT_FAILURE);
    }
    global_payload_size = fread(global_payload, 1, BUFFER_SIZE, file);
    fclose(file);
    snprintf(request, BUFFER_SIZE, request_template, host, global_payload_size-1, global_payload);


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
    
    printf(" Finished in : %f ms\n", experiment_duration);



    // Write latencies to a file
    char log_filename[PATH_MAX]; 
    sprintf(log_filename, "%s/CClient.log", results_directory);
    
    FILE *log_file = fopen(log_filename, "w");
    if (log_file == NULL) {
        perror("Error opening CClient.log");
        pthread_exit(NULL);
    }

    fprintf(log_file, "%f\n", experiment_duration);
    fprintf(log_file, "%d\n", threads_number*workload);


    fclose(log_file);
    free(params_array);
    

    return 0;
}

