import json
import tldextract

class SetToList(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

class DomainData:
    """The output of the crawler. Data is contained in sets, and converted to lists
       for json.dumps(). The purpose is to have unique data only."""

    def __init__(self, netloc):
        p_n = tldextract.extract(netloc)
        self.domain = p_n.domain
        self.suffix = p_n.suffix
        self.subdomain_data = list()
        self._new_subdomain(netloc)
        
    def dumps(self, **kwargs):
        return json.dumps(self.subdomain_data, cls=SetToList, **kwargs)

    def add_page(self, netloc, page):
        sub = self._ensure_subdomain(netloc)
        sub["pages"].append(page)

    def add_phone(self, netloc, phone_number):
        sub = self._ensure_subdomain(netloc)
        sub["phone_numbers"].add(phone_number)

    def add_email(self, netloc, email):
        sub = self._ensure_subdomain(netloc)
        sub["emails"].add(email)

    def add_social(self, netloc, social_media):
        sub = self._ensure_subdomain(netloc)
        sub["social_media"].add(social_media)

    def add_document(self, netloc, document):
        sub = self._ensure_subdomain(netloc)
        sub["documents"].append(document)

    def add_custom_regex(self, netloc, regex):
        sub = self._ensure_subdomain(netloc)
        sub["regex"].add(regex)

    def _new_subdomain(self, netloc):
        # The majority of the data is held within sets to prevent duplicate data.
        self.throw_if_wrong_domain(netloc)
        sub = {"netloc": netloc,
                "pages": list(),        # pages and documents will never get duplicate data, as the crawler will
                "documents": list(),    # never crawl the same link twice
                "emails": set(),
                "phone_numbers": set(),
                "social_media": set(),
                "custom_regex": set(),
                }
        self.subdomain_data.append(sub)
        return sub

    def _retrieve_subdomain(self, netloc):
        for sub in self.subdomain_data:
            if sub["netloc"] == netloc:
                return sub
        return None

    def _ensure_subdomain(self, netloc):
        sub = self._retrieve_subdomain(netloc)
        if sub is None:
            return self._new_subdomain(netloc)
        return sub

    def throw_if_wrong_domain(self, netloc):
        p_n = tldextract.extract(netloc)
        if p_n.domain != self.domain or p_n.suffix != self.suffix:
            raise ValueError("{0} is not a subdomain of {1}.{2}".format(netloc, self.domain, self.suffix))

