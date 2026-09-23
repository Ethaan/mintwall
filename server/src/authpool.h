// Password checks off the network thread (docs/production-plan.md §2).
// A PBKDF2 check costs a few hundred ms of CPU. Logins are parsed on the single asio thread that serves
// every connection, so checking there would stall everyone's packets. Two worker threads do the hashing;
// the login then continues on the dispatcher. The queue is bounded: when full, the login is refused
// ("busy") instead of piling up work.
#ifndef __OTSERV_AUTHPOOL_H__
#define __OTSERV_AUTHPOOL_H__

#include <boost/function.hpp>

namespace authpool {
	// runs `work` on a worker thread; false (and nothing runs) when the queue is full
	bool post(boost::function<void (void)> work);
}

#endif
