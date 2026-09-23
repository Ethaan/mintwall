#include "otpch.h"

#include "passwords.h"
#include "configmanager.h"

#include <openssl/crypto.h>
#include <openssl/evp.h>
#include <openssl/rand.h>

#include <vector>
#include <sstream>
#include <cstdlib>

extern ConfigManager g_config;

namespace {
	const std::string PREFIX = "pbkdf2_sha256$";
	const size_t SALT_BYTES = 16;
	const size_t HASH_BYTES = 32;   // SHA-256 output

	std::string toBase64(const unsigned char* data, size_t len)
	{
		std::vector<unsigned char> out(4 * ((len + 2) / 3) + 1);
		int n = EVP_EncodeBlock(out.data(), data, (int)len);
		return std::string((const char*)out.data(), n);
	}

	bool fromBase64(const std::string& text, std::vector<unsigned char>& out)
	{
		if(text.empty() || text.size() % 4 != 0){
			return false;
		}
		out.resize(3 * text.size() / 4);
		int n = EVP_DecodeBlock(out.data(), (const unsigned char*)text.data(), (int)text.size());
		if(n < 0){
			return false;
		}
		// EVP_DecodeBlock counts the '=' padding as zero bytes
		size_t padding = 0;
		if(text[text.size() - 1] == '='){ padding++; }
		if(text[text.size() - 2] == '='){ padding++; }
		out.resize(n - padding);
		return true;
	}

	bool derive(const std::string& plain, const unsigned char* salt, size_t saltLen, uint32_t iterations,
		unsigned char* out, size_t outLen)
	{
		return PKCS5_PBKDF2_HMAC(plain.data(), (int)plain.size(), salt, (int)saltLen, (int)iterations,
			EVP_sha256(), (int)outLen, out) == 1;
	}

	// "pbkdf2_sha256$<iterations>$<salt>$<hash>" -> parts; false if malformed
	bool parse(const std::string& stored, uint32_t& iterations, std::vector<unsigned char>& salt,
		std::vector<unsigned char>& expected)
	{
		if(stored.compare(0, PREFIX.size(), PREFIX) != 0){
			return false;
		}
		size_t a = PREFIX.size();
		size_t b = stored.find('$', a);
		if(b == std::string::npos){ return false; }
		size_t c = stored.find('$', b + 1);
		if(c == std::string::npos){ return false; }

		std::string iterText = stored.substr(a, b - a);
		if(iterText.empty() || iterText.find_first_not_of("0123456789") != std::string::npos || iterText.size() > 9){
			return false;
		}
		iterations = (uint32_t)std::strtoul(iterText.c_str(), NULL, 10);
		return iterations > 0 && fromBase64(stored.substr(b + 1, c - b - 1), salt) && !salt.empty()
			&& fromBase64(stored.substr(c + 1), expected) && !expected.empty();
	}
}

namespace passwords {
	uint32_t iterations()
	{
		int32_t n = g_config.getNumber(ConfigManager::PASSWORD_ITERATIONS);
		return n > 0 ? (uint32_t)n : 600000;
	}

	bool isPbkdf2(const std::string& stored)
	{
		return stored.compare(0, PREFIX.size(), PREFIX) == 0;
	}

	bool verify(const std::string& plain, const std::string& stored)
	{
		uint32_t iter;
		std::vector<unsigned char> salt, expected;
		if(!parse(stored, iter, salt, expected)){
			return false;
		}
		std::vector<unsigned char> actual(expected.size());
		if(!derive(plain, salt.data(), salt.size(), iter, actual.data(), actual.size())){
			return false;
		}
		return CRYPTO_memcmp(actual.data(), expected.data(), expected.size()) == 0;
	}

	std::string hash(const std::string& plain)
	{
		unsigned char salt[SALT_BYTES];
		unsigned char out[HASH_BYTES];
		uint32_t iter = iterations();
		if(RAND_bytes(salt, (int)sizeof(salt)) != 1 || !derive(plain, salt, sizeof(salt), iter, out, sizeof(out))){
			return "";   // never store a weak hash: the caller keeps the old entry
		}
		std::ostringstream s;
		s << PREFIX << iter << "$" << toBase64(salt, sizeof(salt)) << "$" << toBase64(out, sizeof(out));
		return s.str();
	}

	bool needsRehash(const std::string& stored)
	{
		uint32_t iter;
		std::vector<unsigned char> salt, expected;
		return !parse(stored, iter, salt, expected) || iter < iterations();
	}
}
