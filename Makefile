UNAME_S=$(shell uname -s)
I_MONGO=libmongoc-1.0
I_BSON=libbson-1.0
L_MONGO=mongoc-1.0
L_BSON=bson-1.0

TCP=tcp
SVER=_server
CLNT=_client

ifeq ("$(UNAME_S)", "Darwin")
    $(info "Built under Darwin")
    MONGO_PKG_ROOT=/usr/local/Cellar/mongo-c/1.3.5
else ifeq ("$(UNAME_S)", "Linux")
    $(info "Built under Linux")
    MONGO_PKG_ROOT=/usr/local
endif

ifndef SERVICE_IP
    $(info "SERVICE_IP is not assigned by user, and will be set to 127.0.0.1.")
    SERVICE_IP=127.0.0.1
else
    $(info "SERVICE_IP is set to $(SERVICE_IP).")
endif

ifndef SERVICE_TCP_PORT
    $(info "SERVICE_TCP_PORT is not assigned by user, and will be set to 8000.")
    SERVICE_TCP_PORT=8000
else
    $(info "SERVICE_TCP_PORT is set to $(SERVICE_TCP_PORT).")
endif

all: clean
	gcc -g -o $(TCP)$(CLNT) $(TCP)$(CLNT).c -I$(MONGO_PKG_ROOT)/include/$(I_MONGO) -DSERVICE_IP='"$(SERVICE_IP)"' -DSERVICE_TCP_PORT=$(SERVICE_TCP_PORT) -I$(MONGO_PKG_ROOT)/include/$(I_BSON) -L$(MONGO_PKG_ROOT)/lib -l$(L_MONGO) -l$(L_BSON)
	gcc -g -o $(TCP)$(SVER) $(TCP)$(SVER).c -I$(MONGO_PKG_ROOT)/include/$(I_MONGO) -DSERVICE_IP='"$(SERVICE_IP)"' -DSERVICE_TCP_PORT=$(SERVICE_TCP_PORT) -I$(MONGO_PKG_ROOT)/include/$(I_BSON) -L$(MONGO_PKG_ROOT)/lib -l$(L_MONGO) -l$(L_BSON)

clean:
	if [ -e $(TCP)$(CLNT) ]; then rm $(TCP)$(CLNT); fi
	if [ -e $(TCP)$(SVER) ]; then rm $(TCP)$(SVER); fi
	if [ -d $(TCP)$(CLNT).dSYM ]; then rm -rf $(TCP)$(CLNT).dSYM; fi
	if [ -d $(TCP)$(SVER).dSYM ]; then rm -rf $(TCP)$(SVER).dSYM; fi