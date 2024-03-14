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
#include <stdlib.h> // Para abs()
#include <limits.h>

#define BUFFER_SIZE 1024
#define HTTP_HEADER 74 // it is the size of the header wihtou the length digit
#define MAX_REQUESTS 10000
#define DEBUG_MODE false

// Variáveis globais
char *host;
int port;
char *arquivo_payload;
int threads_number;
int workload;
char global_payload[BUFFER_SIZE]; // Armazenar o conteúdo do payload
char request[BUFFER_SIZE];
char *results_directory;
size_t global_payload_size; // Tamanho do payload

char request_template[] = "POST / HTTP/1.1\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %lu\r\n\r\n%s";

typedef struct {
    int thread_id;
    int socket_id; 
} ThreadParams;




int extract_content_length(const char *response) {
    // Procurar o início do campo "Content-Length"
    const char *content_length_start = strstr(response, "Content-length: ");
    if (content_length_start != NULL) {
        content_length_start += strlen("Content-length: ");

        // Extrair o valor do "Content-Length" como uma string
        char *endptr;
        int content_length = strtol(content_length_start, &endptr, 10);
        if (endptr != content_length_start && *endptr == '\r') {
            return content_length;
        }
    }

    // Se não encontrou o campo "Content-Length" ou o valor não é válido, retorna -1
    return -1;
}

int character_counter(int valor) {
    // Se o valor for 0, precisamos de 1 caractere
    if (valor == 0) {
        return 1;
    }
    // Se o valor for negativo, adicionar 1 para o sinal '-'
    int tamanho = (valor < 0) ? 1 : 0;
    // Calcular o número de dígitos no valor absoluto do número
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

    // Configurar estrutura de endereço
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
        fprintf(stderr, "Erro ao obter informações do host: %s\n", gai_strerror(status));
        pthread_exit(NULL);
    }

    // A estrutura res contém uma lista de endereços; você pode simplesmente usar o primeiro
    server_addr.sin_addr = ((struct sockaddr_in*)res->ai_addr)->sin_addr;
    server_addr.sin_port = htons(port); // Não esqueça de atribuir a porta

    
    
    // Criar e conectar sockets
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Erro ao criar socket");
        pthread_exit(NULL);
    }


    /*struct timeval tv;
    tv.tv_sec = 10000000;  // Timeout de 10 segundos
    tv.tv_usec = 0;  // 0 milissegundos

    // Definir timeout de recebimento
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof tv) < 0) {
        perror("setsockopt SO_RCVTIMEO failed");
    }

    // Definir timeout de envio
    if (setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, (const char*)&tv, sizeof tv) < 0) {
        perror("setsockopt SO_SNDTIMEO failed");
    }*/

    
    // Conectar ao servidor
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Erro ao conectar ao servidor");
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

    // Alocação dinâmica baseada no workload
    double *elapsed_time = (double *)malloc(workload * sizeof(double));
    double *start_timestamp = (double *)malloc(workload * sizeof(double));
    
    // Verifique se a alocação foi bem-sucedida
    if (!elapsed_time || !start_timestamp) {
        perror("Memory allocation error");
        free(elapsed_time); // Libere memória se uma das alocações falhar
        free(start_timestamp);
        pthread_exit(NULL);
    }


    // Establish connection
    // int sockfd = connect_to_server(host, port);

    // Construir requisição
    //char request[BUFFER_SIZE];
    //snprintf(request, BUFFER_SIZE, request_template, host, global_payload_size, global_payload);

    // Buffer para armazenar os dados recebidos
    char response[BUFFER_SIZE];

    magic_socket(sockfd);
    

    // workload = 400;
    // Executar a solicitação
    for (int i = 0; i < workload; i++) {
        //usleep(1000);

        struct timespec start, end;        

        // Medir o tempo de início
        clock_gettime(CLOCK_REALTIME, &start);

        //printf(" - strlen(request) %ld msg:%s \n\n", strlen(request), request);           

        /*for(int i=0; i<=  strlen(request); i++){
            printf(" i: %d and c: %c \n", i, request[i]);           

        }*/



        // Enviar requisição
        if (send(sockfd, request, strlen(request), 0) < 0) {
            perror("Erro ao enviar requisição");
            close(sockfd);
            pthread_exit(NULL);
        }

        // Ler resposta HTTP uma vez
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
            if(total_bytes_recv >= content_length + HTTP_HEADER + digit_length){//tenho de confimrar se nao é =>
                break;
            }


        }

        if(DEBUG_MODE){
            response[total_bytes_recv] = '\0';
            printf(" - Resposta do servidor (recived %ld bytes and expected %d bytes, Thread %d):\n%s\n", total_bytes_recv, ( content_length + HTTP_HEADER + character_counter(content_length)), thread_id, response);           
        }

        if (bytes_recv < 0) {
            perror("Erro ao receber resposta do servidor");
            close(sockfd);
            pthread_exit(NULL);
        } else if (bytes_recv == 0) {
            fprintf(stderr, "Conexão encerrada pelo servidor, workload: %d, threadID: %d\n", i, thread_id );
            close(sockfd);
            sockfd = connect_to_server(host, port); // Reconnect
            magic_socket(sockfd);
            //pthread_exit(NULL);            
            i--; // Retry the same request
        }
        






        // Medir o tempo de fim
        clock_gettime(CLOCK_REALTIME, &end);

        // Calcular o tempo decorrido em milissegundos
        elapsed_time[i] = (end.tv_sec - start.tv_sec) * 1000.0 + (end.tv_nsec - start.tv_nsec) / 1000000.0; 
        double ms_start= start.tv_sec * 1000.0 + start.tv_nsec / 1000000.0;
        start_timestamp[i] = ms_start - ms_ref;
        // start_timestamp[i] =  (start.tv_sec) * 1000.0 + (start.tv_nsec) / 1000000.0; 
    }

    // Fechar socket
    close(sockfd);

    // Escrever latências em um arquivo
    char filename[PATH_MAX]; 
    //sprintf(filename, "/home/ccorreia/tmp/test-proxy/latencias_thread%d.log", thread_id);
    sprintf(filename, "%s/latencias_thread%d.log", results_directory, thread_id);

    FILE *latency_file = fopen(filename, "w");
    if (latency_file == NULL) {
        perror("Erro ao abrir arquivo de latências");
        pthread_exit(NULL);
    }

    fprintf(latency_file, "Timestamp before sending request (ms), elapsed time from sending to receiving the reposnse (ms)\n");
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

//Para isto funcionar eu tive que mudar uma linha no SubstrateVMProxy.java para nao ter queue full : this.queue = new ArrayBlockingQueue<>(256);
// example: ./http_post 146.193.41.25 8080 payload.post 256 1000  /home/intelnuc2/Downloads/graal_test/tmp/
// ./http_post 146.193.41.25 8080 /home/intelnuc2/Downloads/graal_test/toDelete/http-loader/payload.post 256 8192 /home/intelnuc2/Downloads/graal_test/toDelete/http-loader/results/

// make clean && make && ./http_post 146.193.41.25 8080 payload.post 256 8192  /home/ccorreia/work/argo/benchmarks/http-loader/results/
// make clean && make && ./http_post 146.193.41.25 8080 payload.post 256 8192  /home/intelnuc2/Downloads/graal_test/tmp/
// make clean && make && ./http_post 146.193.41.25 8080 payload.post 256 8192  /home/ccorreia/graal_test/tmp/

int main(int argc, char *argv[]) {
    if (argc != 7) {
        fprintf(stderr, "Uso: %s <host> <porta> <arquivo_payload> <#threads> <workload> <results_directory>\n", argv[0]);
        exit(EXIT_FAILURE);
    }




/*   fprintf(stderr, "\n\n\nRunning, tap enter to exit.\n");
    getchar();
    printf("Exit. ");
    return 0;
*/

    
    // Atribuir valores para as variáveis globais
    host = argv[1];
    port = atoi(argv[2]);
    arquivo_payload = argv[3];
    threads_number = atoi(argv[4]);
    workload = atoi(argv[5]);
    results_directory = argv[6];
    struct timespec global_start, global_end;


    
    // Abrir e ler o conteúdo do arquivo de payload uma única vez
    FILE *file = fopen(argv[3], "r");
    if (file == NULL) {
        perror("Erro ao abrir arquivo de payload");
        exit(EXIT_FAILURE);
    }
    global_payload_size = fread(global_payload, 1, BUFFER_SIZE, file);
    fclose(file);
    snprintf(request, BUFFER_SIZE, request_template, host, global_payload_size-1, global_payload);


    printf(" Running with workload: %d\n", threads_number);

    pthread_t threads[threads_number];



    ThreadParams *params_array = malloc(threads_number * sizeof(ThreadParams));
    if (params_array == NULL) {
        perror("Erro ao alocar memória para os parâmetros das threads");
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
            perror("Erro ao aguardar thread");
            exit(EXIT_FAILURE);
        }
    }

    // Medir o tempo de fim
    clock_gettime(CLOCK_MONOTONIC, &global_end);

    // Calcular o tempo decorrido em milissegundos
    double experiment_duration = (global_end.tv_sec - global_start.tv_sec) * 1000.0 + (global_end.tv_nsec - global_start.tv_nsec) / 1000000.0;
    
    printf(" Finished in : %f ms\n", experiment_duration);



    // Escrever latências em um arquivo
    char log_filename[PATH_MAX]; 
    sprintf(log_filename, "%s/CClient.log", results_directory);
    
    FILE *log_file = fopen(log_filename, "w");
    if (log_file == NULL) {
        perror("Erro ao abrir CClient.log");
        pthread_exit(NULL);
    }

    fprintf(log_file, "%f\n", experiment_duration);
    fprintf(log_file, "%d\n", threads_number*workload);


    fclose(log_file);
    free(params_array);
    

    return 0;
}

