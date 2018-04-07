MODULE=server
SRCDIR=oar

OARDIR_BINFILES = $(SRCDIR)/tools/oar_resources_init \
		  $(SRCDIR)/tools/oar_resources_add
		  # $(SRCDIR)/modules/scheduler/oar_all_in_one_scheduler \
		  # $(SRCDIR)/qfunctions/oarnotify \
		  # $(SRCDIR)/qfunctions/oarqueue \
		  # $(SRCDIR)/qfunctions/oarremoveresource \
		  # $(SRCDIR)/qfunctions/oaraccounting \
		  # $(SRCDIR)/qfunctions/oarproperty \
		  # $(SRCDIR)/qfunctions/oaradmissionrules \
		  # $(SRCDIR)/qfunctions/oarmonitor \
		  # $(SRCDIR)/modules/runner/bipbip.in \
		  # $(SRCDIR)/tools/oar_resources_init \
		  # $(SRCDIR)/tools/oar_resources_add

OARCONFDIR_BINFILES = $(SRCDIR)/tools/oar_phoenix.pl

SBINDIR_FILES = setup/server/oar-server.in

SHAREDIR_FILES = $(SRCDIR)/tools/job_resource_manager.pl \
                   $(SRCDIR)/tools/job_resource_manager_cgroups.pl \
		   $(SRCDIR)/tools/suspend_resume_manager.pl \
		   $(SRCDIR)/tools/oarmonitor_sensor.pl \
		   $(SRCDIR)/../scripts/server_epilogue \
		   $(SRCDIR)/../scripts/server_prologue \
		   $(SRCDIR)/tools/wake_up_nodes.sh \
		   $(SRCDIR)/tools/shut_down_nodes.sh \
		   #$(SRCDIR)/modules/scheduler/scheduler_quotas.conf

DEFAULTDIR_FILES = setup/default/oar-server.in

INITDIR_FILES = setup/init.d/oar-server.in

CRONDIR_FILES = setup/cron.d/oar-server.in

include Makefiles/shared/shared.mk

clean: clean_shared
	# $(OARDO_CLEAN) CMD_WRAPPER=$(OARDIR)/Almighty CMD_TARGET=$(DESTDIR)$(SBINDIR)/Almighty
	# $(OARDO_CLEAN) CMD_WRAPPER=$(OARDIR)/oarnotify CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarnotify
	# $(OARDO_CLEAN) CMD_WRAPPER=$(OARDIR)/oarqueue CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarqueue
	# $(OARDO_CLEAN) CMD_WRAPPER=$(OARDIR)/oarremoveresource CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarremoveresource
	# $(OARDO_CLEAN) CMD_WRAPPER=$(OARDIR)/oaraccounting CMD_TARGET=$(DESTDIR)$(SBINDIR)/oaraccounting
	# $(OARDO_CLEAN) CMD_WRAPPER=$(OARDIR)/oarproperty CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarproperty
	# $(OARDO_CLEAN) CMD_WRAPPER=$(OARDIR)/oaradmissionrules CMD_TARGET=$(DESTDIR)$(SBINDIR)/oaradmissionrules
	# $(OARDO_CLEAN) CMD_WRAPPER=$(OARDIR)/oarmonitor CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarmonitor
	$(OARDO_CLEAN) CMD_WRAPPER=$(OARDIR)/oar_resources_init CMD_TARGET=$(DESTDIR)$(SBINDIR)/oar_resources_init
	$(OARDO_CLEAN) CMD_WRAPPER=$(OARDIR)/oar_resources_add CMD_TARGET=$(DESTDIR)$(SBINDIR)/oar_resources_add
	$(OARDO_CLEAN) CMD_WRAPPER=$(OARCONFDIR)/oar_phoenix.pl CMD_TARGET=$(DESTDIR)$(SBINDIR)/oar_phoenix	

build: build_shared
	$(OARDO_BUILD) CMD_WRAPPER=$(OARDIR)/oar_resources_init CMD_TARGET=$(DESTDIR)$(SBINDIR)/oar_resources_init
	$(OARDO_BUILD) CMD_WRAPPER=$(OARDIR)/oar_resources_add CMD_TARGET=$(DESTDIR)$(SBINDIR)/oar_resources_add
	$(OARDO_BUILD) CMD_WRAPPER=$(OARCONFDIR)/oar_phoenix.pl CMD_TARGET=$(DESTDIR)$(SBINDIR)/oar_phoenix	

install: build install_shared
	# pip install .
	install -d $(DESTDIR)$(OARCONFDIR)
	install -m 0750 $(OARCONFDIR_BINFILES) $(DESTDIR)$(OARCONFDIR)
	for file in oar3-almighty oar3-appendice-proxy oar3-bipbip-commander \
		oar3-sarko oar3-finaud oar3-leon oar3-bipbip oar3-node-change-state \
		oar3-hulot kao kamelot kamelot-fifo;\
	do \
		mv $(DESTDIR)$(BINDIR)/$$file $(DESTDIR)$(OARDIR)/$$file; \
	done

	$(OARDO_INSTALL) CMD_WRAPPER=$(DESTDIR)$(OARDIR)/oar3-almighty CMD_TARGET=$(DESTDIR)$(SBINDIR)/almighty

	# $(OARDO_INSTALL) CMD_WRAPPER=$(OARDIR)/Almighty CMD_TARGET=$(DESTDIR)$(SBINDIR)/Almighty
	# $(OARDO_INSTALL) CMD_WRAPPER=$(OARDIR)/oarnotify CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarnotify
	# $(OARDO_INSTALL) CMD_WRAPPER=$(OARDIR)/oarqueue CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarqueue
	# $(OARDO_INSTALL) CMD_WRAPPER=$(OARDIR)/oarremoveresource CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarremoveresource
	# $(OARDO_INSTALL) CMD_WRAPPER=$(OARDIR)/oaraccounting CMD_TARGET=$(DESTDIR)$(SBINDIR)/oaraccounting
	# $(OARDO_INSTALL) CMD_WRAPPER=$(OARDIR)/oarproperty CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarproperty
	# $(OARDO_INSTALL) CMD_WRAPPER=$(OARDIR)/oaradmissionrules CMD_TARGET=$(DESTDIR)$(SBINDIR)/oaradmissionrules
	# $(OARDO_INSTALL) CMD_WRAPPER=$(OARDIR)/oarmonitor CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarmonitor
	$(OARDO_INSTALL) CMD_WRAPPER=$(OARDIR)/oar_resources_init CMD_TARGET=$(DESTDIR)$(SBINDIR)/oar_resources_init
	$(OARDO_INSTALL) CMD_WRAPPER=$(OARDIR)/oar_resources_add CMD_TARGET=$(DESTDIR)$(SBINDIR)/oar_resources_add
	$(OARDO_INSTALL) CMD_WRAPPER=$(OARCONFDIR)/oar_phoenix.pl CMD_TARGET=$(DESTDIR)$(SBINDIR)/oar_phoenix

uninstall: uninstall_shared
	# @for file in $(OARCONFDIR_FILES); do rm -f $(DESTDIR)$(OARCONFDIR)/`basename $$file`; done
	# rm -f $(DESTDIR)$(OARDIR)/Almighty
	# rm -f $(DESTDIR)$(OARDIR)/Leon
	# rm -f $(DESTDIR)$(OARDIR)/sarko
	# rm -f $(DESTDIR)$(OARDIR)/finaud
	# rm -f $(DESTDIR)$(OARDIR)/NodeChangeState

	# rm -rf $(DESTDIR)$(EXAMPLEDIR)

	$(OARDO_UNINSTALL) CMD_WRAPPER=$(DESTDIR)$(BINDIR)/oar3-almighty CMD_TARGET=$(DESTDIR)$(SBINDIR)/almighty

	# $(OARDO_UNINSTALL) CMD_WRAPPER=$(OARDIR)/oarnotify CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarnotify
	# $(OARDO_UNINSTALL) CMD_WRAPPER=$(OARDIR)/oarqueue CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarqueue
	# $(OARDO_UNINSTALL) CMD_WRAPPER=$(OARDIR)/oarremoveresource CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarremoveresource
	# $(OARDO_UNINSTALL) CMD_WRAPPER=$(OARDIR)/oaraccounting CMD_TARGET=$(DESTDIR)$(SBINDIR)/oaraccounting
	# $(OARDO_UNINSTALL) CMD_WRAPPER=$(OARDIR)/oarproperty CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarproperty
	# $(OARDO_UNINSTALL) CMD_WRAPPER=$(OARDIR)/oaradmissionrules CMD_TARGET=$(DESTDIR)$(SBINDIR)/oaradmissionrules
	# $(OARDO_UNINSTALL) CMD_WRAPPER=$(OARDIR)/oarmonitor CMD_TARGET=$(DESTDIR)$(SBINDIR)/oarmonitor

	$(OARDO_UNINSTALL) CMD_WRAPPER=$(OARDIR)/oar_resources_init CMD_TARGET=$(DESTDIR)$(SBINDIR)/oar_resources_init
	$(OARDO_UNINSTALL) CMD_WRAPPER=$(OARDIR)/oar_resources_add CMD_TARGET=$(DESTDIR)$(SBINDIR)/oar_resources_add
	$(OARDO_UNINSTALL) CMD_WRAPPER=$(OARCONFDIR)/oar_phoenix.pl CMD_TARGET=$(DESTDIR)$(SBINDIR)/oar_phoenix	

.PHONY: install setup uninstall build clean
