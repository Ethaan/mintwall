// Background save writer (docs/production-plan.md §3c).
// Saves are captured on the game thread as SQL (DBBatch, memory only) and written here, on one thread with
// its own SQLite connection, one transaction per batch - so the disk never holds up the game. Batches are
// written in the order they were posted (a logout after a server save wins), and a login waits only for
// that player's pending writes.
#ifndef __OTSERV_DBWRITER_H__
#define __OTSERV_DBWRITER_H__

#include <stdint.h>

struct DBBatch;

namespace dbwriter {
	// queue a captured batch; the writer owns and deletes it
	void post(DBBatch* batch);
	// block until no queued batch holds this player (a login must read their newest save)
	void waitFor(uint32_t guid);
	// block until everything queued is written (shutdown)
	void flush();
}

#endif
