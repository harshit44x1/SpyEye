#ifndef ATTACK_METHOD_H
#define ATTACK_METHOD_H

#include "esp_wifi_types.h"


void attack_method_broadcast(const wifi_ap_record_t *ap_record, unsigned period_sec);


void attack_method_broadcast_stop();


void attack_method_rogueap(const wifi_ap_record_t *ap_record);

#endif
