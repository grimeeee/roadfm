package com.roadfm.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@ConfigurationPropertiesScan
public class RoadFmApplication {
    public static void main(String[] args) {
        SpringApplication.run(RoadFmApplication.class, args);
    }
}
