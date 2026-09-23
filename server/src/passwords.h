// Salted PBKDF2 password hashes (docs/production-plan.md §2).
// Stored as "pbkdf2_sha256$<iterations>$<salt base64>$<hash base64>" - the same format
// tools/provision-accounts.py writes with Python's hashlib.pbkdf2_hmac.
#ifndef __OTSERV_PASSWORDS_H__
#define __OTSERV_PASSWORDS_H__

#include <string>
#include <stdint.h>

namespace passwords {
	// config.lua PasswordIterations (OWASP 2023 for PBKDF2-HMAC-SHA256: 600,000)
	uint32_t iterations();

	bool isPbkdf2(const std::string& stored);
	// constant-time check of a pbkdf2_sha256 entry; false for anything malformed
	bool verify(const std::string& plain, const std::string& stored);
	// a new entry with a fresh random salt
	std::string hash(const std::string& plain);
	// legacy (plain / md5 / sha1) entries, or fewer iterations than configured, get rehashed on login
	bool needsRehash(const std::string& stored);
}

#endif
