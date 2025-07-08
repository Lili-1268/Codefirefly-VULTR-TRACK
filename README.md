# Codefirefly-VULTR-TRACK

This project helps companies find new customers more easily. Users searching for potential clients can specify the industry they’re interested in. Based on this input, the system provides relevant suggestions and displays their locations on a map. 

## Companies per sector

The LLaMA model, accessed via the GROQ API, is used to generate customer suggestions.

The specific model in use is LLaMA 3-8B-8192.

An API key for GROQ has been previously created and configured.

## MAP 

The map is generated using the OpenCage Data API, which provides geolocation information. The customer's location is then displayed on an interactive map.

## Contact search

Hunter.io is used to find contact persons within a company.
An API key allows for seamless integration with their database. By providing a domain name, the API can return the email addresses of specific individuals associated with that organization.

## Deployment 

The app is deployed using Flask on a Vultr server. The Vultr server has the following specifications:

    vCPU: 1 vCPU

    RAM: 4096 MB (4 GB)

    Storage: 30 GB NVMe

    Operating System: Ubuntu 22.04 x64
