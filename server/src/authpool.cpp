#include "otpch.h"

#include "authpool.h"

#include <boost/asio/post.hpp>
#include <boost/bind/bind.hpp>
#include <boost/asio/thread_pool.hpp>
#include <boost/atomic.hpp>

namespace {
	const int WORKERS = 2;
	const int MAX_PENDING = 32;    // queued + running checks

	boost::atomic<int> pending(0);

	boost::asio::thread_pool& pool()
	{
		// never destroyed: joining at static destruction could hang on a pending check
		static boost::asio::thread_pool* p = new boost::asio::thread_pool(WORKERS);
		return *p;
	}

	void run(boost::function<void (void)> work)
	{
		try{
			work();
		}
		catch(...){
		}
		--pending;
	}
}

namespace authpool {
	bool post(boost::function<void (void)> work)
	{
		if(++pending > MAX_PENDING){
			--pending;
			return false;
		}
		boost::asio::post(pool(), boost::bind(&run, work));
		return true;
	}
}
