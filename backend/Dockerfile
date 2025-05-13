FROM python:3.10-slim

# 1) Make /app the working dir for everything
WORKDIR /app

# 2) Arduino-CLI + ESP32 setup
RUN apt-get update && apt-get install -y curl unzip git && rm -rf /var/lib/apt/lists/*  

# Install Arduino CLI
RUN curl -fsSL https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_64bit.tar.gz \
    | tar -xz -C /usr/local/bin arduino-cli

# Set up Arduino CLI config with ESP32 support and no timeout
RUN arduino-cli config init && \
arduino-cli config set network.connection_timeout 0 && \
arduino-cli config board --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json 


# Install ESP32 platform and required Arduino libraries
RUN arduino-cli core update-index --config-file /root/.arduino15/arduino-cli.yaml && \
    arduino-cli core install esp32:esp32 --config-file /root/.arduino15/arduino-cli.yaml && \
    arduino-cli lib update-index --config-file /root/.arduino15/arduino-cli.yaml && \
    arduino-cli lib install "WiFiManager" "GxEPD2" "Adafruit GFX Library" "Adafruit BusIO" --config-file /root/.arduino15/arduino-cli.yaml


# epd_driver clone
RUN mkdir -p /root/Arduino/libraries && \
    git clone https://github.com/ZinggJM/GxEPD2.git /root/Arduino/libraries/epd_driver

# Install LilyGo EPD47 library (includes epd_driver.h)
RUN git clone https://github.com/Xinyuan-LilyGO/LilyGo-EPD47.git /root/Arduino/libraries/LilyGo-EPD47

# 3) Pull in your Python deps and code at /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

EXPOSE 5000
CMD ["python", "main.py"]
