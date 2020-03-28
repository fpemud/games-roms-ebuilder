prefix=/usr

all:

install:
	install -d -m 0755 "$(DESTDIR)/$(prefix)/bin"
	cp -r src/* "$(DESTDIR)/$(prefix)/bin"

.PHONY: all clean install
