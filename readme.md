# Monitorování stavu baterie pomocí BLE
Školní projekt pro předmět SMAP. Cílem projektu je vytvoření scriptu, který monitoruje stav baterie BLE bezdrátových zařízení v domácnosti.

## Požadavky
* Python 3
* Zařízení s Linuxem a podporou BLE komunikace, na kterém budou scripty spouštěny (například Raspberry Pi)
* Alespoň jedno BLE zařízení, které poskytuje informaci o stavu baterie

## Instalace
Nejdříve je nutné získání potřebných Python 3 modulů. V případě problému při instalaci jsou další informace k dispozici v jednotlivých repositářích modulů.

### bluepy ([GitHub](https://github.com/IanHarvey/bluepy))
Modul poskytující přehledné API pro BLE komunikaci.
```sh
sudo apt-get install python3-pip libglib2.0-dev
sudo pip3 install bluepy
```

### pyttsx3 ([GitHub](https://github.com/nateshmbhat/pyttsx3))
Modul pro offline text to speech potřebný pro hlasové upozorňování.
```sh
sudo pip3 install pyttsx3
```

### Ostatní použité moduly
Všechny by měly být součástí Python 3.
* os
* time
* datetime
* json

## Konfigurace
Konfigurace je řešena pomocí následujících JSON souborů.

### config.json
Nastavení týkající se monitorování, které má parametry:

* monitoringFrequency - frekvence spouštění monitorování zařízení v sekundách (číslo)
* batteryLevelAlert - úroveň baterie, při které bude uživatel upozorňován (číslo 0 - 90)
* speechLanguage - jazyk používaný pro hlasové upozorňování (string)
    * v základu pouze "czech" a "english", možné rozšíření v localization.json
* nightMode - vypnutí upozorňování přes noc (bool)

### localization.json
Soubor obsahující lokalizační stringy. V základu pouze česká a anglická lokalizace. Pro podporu nového jazyka je potřeba přidat nový parametr s názvem jazyka a následně upravit lokalizační stringy. Ponechání parametru #device_name# je nutné pro správné upozorňování.

### devices.json
Soubor obsahující údaje monitorovaných zařízení. Soubor je nutné manuálně upravit na základě výsledků scriptu **discover.py** z následující kapitoly.

Příklad konfigurace (s popisky):
```sh
{
  Pole monitorovaných zařízení
  "devices": [{
      MAC adresa zařízení
      "address": "01:02:03:04:05:06",
      Typ adresy zařízení (public nebo random)
      "addressType": "random",
      Jméno zařízení použité při hlasovém upozornění
      "friendlyName": "Moje zařízení",
      ID služby baterie (pokud není k dispozici, tak se použije defaultní)
      "batteryServiceUuid": "180f",
      ID charakteristiky úrovně baterie (pokud není k dispozici, tak se použije defaultní)
      "batteryCharacteristicUuid": "2a19"
    }]
}
```

## Spuštění
Všechny scripty je nutné spouštět jako **root** pro správnou BLE funkcionalitu. Projekt obsahuje dva hlavní scripty:

### discover.py
Script vyhledávající všechna BLE zařízení v okolí. Výsledek vyhledávání je ukládán ve složce discoveries do JSON souborů ve formátu "discovery-timestamp.json". Script slouží pro snadné vytvoření konfiguračního souboru **devices.json** z předchozí kapitoly.

Příklad nalezeného zařízení (s popisky):
```sh
{
  Pole nalezených zařízení
  "devices": [{
      MAC adresa zařízení
      "address": "01:02:03:04:05:06",
      Typ adresy zařízení (public nebo random)
      "addressType": "random",
      Síla signálu (dBm)
      "rssi": -42,
      Příznak říkající, zda je zařízení aktuálně v připojitelném stavu
      "connectable": true,
      Pole informací, které zařízení vysílá při své propagaci
      "advertising_data": [{
          ID položky
          "adtype": 9,
          Popis položky (string pokud je ID podle BLE konvence, jinak HEX)
          "description": "Complete Local Name",
          Hodnota položky
          "value": "Example Device"
        }],
      Pole služeb, které zařízení poskytuje
      "services": [{
          ID služby (string pokud je UUID podle BLE konvence, jinak HEX)
          "uuid": "Example Service",
          Pole charakteristik, které služba poskytuje
          "characteristics": [{
              ID charakteristiky (string pokud je UUID podle BLE konvence, jinak HEX)
              "uuid": "Example Characteristic",
              ID nabízených funkcí
              "properties": 10,
              Nabízené funkce
              "propertiesString": "READ",
              Příznak, zda charakteristika nabízí read
              "supportsRead": true
            }]
...
```

### monitor.py
Script monitorující úroveň baterie zařízení definovaných v souboru **devices.json**. Po spuštění dochází k monitorování v nekonečné smyčce s frekvencí podle konfigurace. V případě zjištění slabé baterie nebo plně nabitého zařízení, které bylo doposud nabíjené, dojde k hlasovému upozornění. Dodatečné informace jsou vypisovány do konzole.