FROM php:8.2-apache

# Install the mysqli extension so index.php can talk to MySQL
RUN docker-php-ext-install mysqli

# Run as a non-root user where possible (Apache still needs to bind :80 as root
# initially, but www-data serves the actual requests, matching Section 16 -
# "containers run as non-root users wherever the base image allows it")
RUN a2enmod headers

# Copy site content
COPY ./public/ /var/www/html/

# Ensure robots.txt and the hidden admin path are readable by the webserver
RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
