test:
	python setup.py test

release:
	python setup.py sdist upload

build_docs:
	sphinx-build -b html docs/ docs/_build/

BUILDROOT=build

help:
	@echo "You need to read the Makefile to know what to build"
	@echo "Targets to build debian packages: locustio.git"

clean:
	$(RM) *~ *.in/*~
	$(RM) build/*.deb build/*.changes build/*.dsc build/*-fsio*.tar.*
	$(RM) -r build/locustio.git

distclean:
	$(RM) -r build/

###########################
# LocustIO  (originally from    https://github.com/locustio/locust.git)
# Define which branch to build from. master, develop...
LOCUST_BRANCH=master
LOCUST_COMMIT=54e011f7d375451e5ebd324ba2a342e48faef308
LOCUST_BUILD_DIR=$(BUILDROOT)/locustio.git

$(LOCUST_BUILD_DIR):
	mkdir -p $(BUILDROOT)
	git clone --recursive --branch $(LOCUST_BRANCH) https://github.com/locustio/locust.git $@
	cd $@ ; git reset --hard $(LOCUST_COMMIT)

# Update the package version to git-id (do this _always_)
.PHONY: $(LOCUST_BUILD_DIR)/locust/__init__.py
$(LOCUST_BUILD_DIR)/locust/__init__.py: $(LOCUST_BUILD_DIR)
	perl -i.bak -pe "s/version = .*/version = '$(shell cd $< ; git describe --tags)'/" $(LOCUST_BUILD_DIR)/locust/__init__.py
	perl -i.bak -pe "s/version = .*/version = '$(shell cd $< ; git describe --tags)'/" $(LOCUST_BUILD_DIR)/setup.py


# Apply patches
$(LOCUST_BUILD_DIR)/.patched: $(LOCUST_BUILD_DIR)
	echo "supply the patch in here:: patch -p1 < tims_patch_file.patch"
	touch $@

locustio.git: $(LOCUST_BUILD_DIR) $(LOCUST_BUILD_DIR)/locust/__init__.py $(LOCUST_BUILD_DIR)/.patched
	cd $< && python setup.py --command-packages=stdeb.command bdist_deb
	mv $</deb_dist/python-locustio_$(shell cd $< ; git describe --tags)-1_all.deb .
	@echo "git add python-locustio_$(shell cd $< ; git describe --tags)-1_all.deb"
	@echo "Remember to run git rm for old python-locustio package and make the update in one single commit."

##############################
# Common target for all packages in this directory
deb: locustio.git

.PHONY: locustio.git
