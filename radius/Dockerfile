FROM freeradius/freeradius-server:latest-3.2

COPY clients.conf /etc/raddb/clients.conf
COPY rest /etc/raddb/mods-available/rest
COPY default /etc/raddb/sites-available/default
COPY inner-tunnel /etc/raddb/sites-available/inner-tunnel

# Enable rest module
RUN ln -sf /etc/raddb/mods-available/rest /etc/raddb/mods-enabled/rest
