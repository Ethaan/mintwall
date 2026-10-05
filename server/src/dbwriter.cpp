#include "otpch.h"

#include "dbwriter.h"
#include "database.h"
#include "databasesqlite.h"
#include "configmanager.h"
#include "tools.h"
#include "otsystem.h"

#include <sqlite3.h>
#include <boost/thread.hpp>

#include <deque>
#include <map>
#include <iostream>

extern ConfigManager g_config;

namespace {
	boost::mutex lock;
	boost::condition_variable changed;
	std::deque<DBBatch*> queue;
	std::map<uint32_t, int32_t> pending;     // guid -> queued batches holding it
	bool writing = false;
	sqlite3* handle = NULL;
	boost::thread* worker = NULL;

	bool run(const std::string& sql)
	{
		std::string buf = DatabaseSQLite::_parse(sql);
		char* error = NULL;
		if(sqlite3_exec(handle, buf.c_str(), NULL, NULL, &error) != SQLITE_OK){
			std::cout << "> Save writer: SQLITE ERROR: " << (error ? error : "?") << " (" << buf.substr(0, 200) << ")"
				<< std::endl;
			sqlite3_free(error);
			return false;
		}
		return true;
	}

	void write(DBBatch* batch)
	{
		int64_t start = OTSYS_TIME();
		bool ok = run("BEGIN IMMEDIATE");
		for(size_t i = 0; ok && i < batch->queries.size(); ++i){
			ok = run(batch->queries[i]);
		}
		ok = ok && run("COMMIT");
		if(!ok){
			run("ROLLBACK");
			std::cout << "> Server save FAILED: " << batch->guids.size() << " player(s) not written" << std::endl;
		}
		else if(batch->serverSave){
			std::cout << "> Server saved in " << batch->captureMs << " ms (" << batch->guids.size() << " players, "
				<< batch->houses << (batch->allHouses ? " houses (all)" : " changed houses") << ", "
				<< batch->houseInfos << " house infos in " << batch->mapMs
				<< " ms; written in " << (OTSYS_TIME() - start) << " ms)" << std::endl;
		}
	}

	void loop()
	{
		while(true){
			DBBatch* batch;
			{
				boost::mutex::scoped_lock l(lock);
				while(queue.empty()){
					changed.wait(l);
				}
				batch = queue.front();
				writing = true;
			}

			write(batch);

			{
				boost::mutex::scoped_lock l(lock);
				queue.pop_front();
				writing = false;
				for(size_t i = 0; i < batch->guids.size(); ++i){
					if(--pending[batch->guids[i]] <= 0){
						pending.erase(batch->guids[i]);
					}
				}
			}
			changed.notify_all();
			delete batch;
		}
	}

	void start()
	{
		// its own connection: the game's connection keeps reading (WAL) while a batch is written
		if(sqlite3_open(g_config.getString(ConfigManager::SQL_DB).c_str(), &handle) != SQLITE_OK){
			std::cout << "> Save writer: cannot open the database - saves will fail" << std::endl;
		}
		sqlite3_exec(handle, "PRAGMA journal_mode = WAL; PRAGMA synchronous = NORMAL;", NULL, NULL, NULL);
		sqlite3_busy_timeout(handle, 5000);
		worker = new boost::thread(&loop);
	}
}

namespace dbwriter {
	void post(DBBatch* batch)
	{
		{
			boost::mutex::scoped_lock l(lock);
			if(!worker){
				start();
			}
			for(size_t i = 0; i < batch->guids.size(); ++i){
				++pending[batch->guids[i]];
			}
			queue.push_back(batch);
		}
		changed.notify_all();
	}

	void waitFor(uint32_t guid)
	{
		boost::mutex::scoped_lock l(lock);
		while(pending.find(guid) != pending.end()){
			changed.wait(l);
		}
	}

	void flush()
	{
		boost::mutex::scoped_lock l(lock);
		while(!queue.empty() || writing){
			changed.wait(l);
		}
	}
}
