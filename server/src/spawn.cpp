//////////////////////////////////////////////////////////////////////
// OpenTibia - an opensource roleplaying game
//////////////////////////////////////////////////////////////////////
//
//////////////////////////////////////////////////////////////////////
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software Foundation,
// Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
//////////////////////////////////////////////////////////////////////
#include "otpch.h"

#include "spawn.h"
#include "game.h"
#include "player.h"
#include "npc.h"
#include "tools.h"
#include "configmanager.h"

#include <libxml/xmlmemory.h>
#include <libxml/parser.h> 

extern ConfigManager g_config;
extern Monsters g_monsters;
extern Game g_game;

#define MINSPAWN_INTERVAL 10000

Spawns::Spawns()
{
	loaded = false;
	started = false;
	filename = "";
}

Spawns::~Spawns()
{
	clear();
}

bool Spawns::loadFromXml(const std::string& _filename)
{
	if(isLoaded()){
		return true;
	}

	filename = _filename;
	xmlDocPtr doc = xmlParseFile(filename.c_str());

	if(doc){
		xmlNodePtr root, spawnNode;
		root = xmlDocGetRootElement(doc);

		if(xmlStrcmp(root->name,(const xmlChar*)"spawns") != 0){
			xmlFreeDoc(doc);
			return false;
		}

		int intValue;
		std::string strValue;

		spawnNode = root->children;
		while(spawnNode){
			if(xmlStrcmp(spawnNode->name, (const xmlChar*)"spawn") == 0){
				Position centerPos;
				int32_t radius = -1;

				if(readXMLInteger(spawnNode, "centerx", intValue)){
					centerPos.x = intValue;
				}
				else{
					xmlFreeDoc(doc);
					return false;
				}

				if(readXMLInteger(spawnNode, "centery", intValue)){
					centerPos.y = intValue;
				}
				else{
					xmlFreeDoc(doc);
					return false;
				}

				if(readXMLInteger(spawnNode, "centerz", intValue)){
					centerPos.z = intValue;
				}
				else{
					xmlFreeDoc(doc);
					return false;
				}

				if(readXMLInteger(spawnNode, "radius", intValue)){
					radius = intValue;
				}
				else{
					xmlFreeDoc(doc);
					return false;
				}

				Spawn* spawn = new Spawn(centerPos, radius);
				spawnList.push_back(spawn);

				xmlNodePtr tmpNode = spawnNode->children;
				while(tmpNode){
					if(xmlStrcmp(tmpNode->name, (const xmlChar*)"monster") == 0){

						std::string name = "";
						Position pos = centerPos;
						Direction dir = NORTH;
						uint32_t interval = 0;

						if(readXMLString(tmpNode, "name", strValue)){
							name = strValue;
						}
						else{
							tmpNode = tmpNode->next;
							continue;
						}

						if(readXMLInteger(tmpNode, "direction", intValue)){
							switch(intValue){
								case 0: dir = NORTH; break;
								case 1: dir = EAST; break;
								case 2: dir = SOUTH; break;
								case 3: dir = WEST; break;
							}
						}

						if(readXMLInteger(tmpNode, "x", intValue)){
							pos.x += intValue;
						}
						else{
							tmpNode = tmpNode->next;
							continue;
						}

						if(readXMLInteger(tmpNode, "y", intValue)){
							pos.y += intValue;
						}
						else{
							tmpNode = tmpNode->next;
							continue;
						}

						if(readXMLInteger(tmpNode, "spawntime", intValue) || readXMLInteger(tmpNode, "interval", intValue)){
							interval = intValue * 1000;
						}
						else{
							tmpNode = tmpNode->next;
							continue;
						}
						
						if(interval >= MINSPAWN_INTERVAL){
							spawn->addMonster(name, pos, dir, interval);
						}
						else{
							std::cout << "[Warning] Spawns::loadFromXml " << name << " " << pos << " spawntime can not be less than " << MINSPAWN_INTERVAL / 1000 << " seconds." << std::endl;
						}
					}
					else if(xmlStrcmp(tmpNode->name, (const xmlChar*)"npc") == 0){

						Direction direction = NORTH;
						std::string name = "";
						Position placePos = centerPos;

						if(readXMLString(tmpNode, "name", strValue)){
							name = strValue;
						}
						else{
							tmpNode = tmpNode->next;
							continue;
						}

						if(readXMLInteger(tmpNode, "direction", intValue)){
							switch(intValue){
								case 0: direction = NORTH; break;
								case 1: direction = EAST; break;
								case 2: direction = SOUTH; break;
								case 3: direction = WEST; break;
							}
						}

						if(readXMLInteger(tmpNode, "x", intValue)){
							placePos.x += intValue;
						}
						else{
							tmpNode = tmpNode->next;
							continue;
						}

						if(readXMLInteger(tmpNode, "y", intValue)){
							placePos.y += intValue;
						}
						else{
							tmpNode = tmpNode->next;
							continue;
						}

						Npc* npc = Npc::createNpc(name);
						if(!npc){
							tmpNode = tmpNode->next;
							continue;
						}

						npc->setDirection(direction);
						npc->setMasterPos(placePos, radius);
						npcList.push_back(npc);
					}

					tmpNode = tmpNode->next;
				}
			}

			spawnNode = spawnNode->next;
		}

		xmlFreeDoc(doc);
		loaded = true;
		return true;
	}

	return false;
}

void Spawns::startup()
{	
	if(!isLoaded() || isStarted())
		return;
		
	for(NpcList::iterator it = npcList.begin(); it != npcList.end(); ++it){
        g_game.placeCreature((*it), (*it)->getMasterPos(), false, true);
    }
    npcList.clear();

	for(SpawnList::iterator it = spawnList.begin(); it != spawnList.end(); ++it){
		(*it)->startup();
	}

	started = true;
}

void Spawns::clear()
{
	for(SpawnList::iterator it= spawnList.begin(); it != spawnList.end(); ++it){
		delete (*it);
	}

	spawnList.clear();

	loaded = false;
	started = false;
	filename = "";
}

bool Spawns::isInZone(const Position& centerPos, int32_t radius, const Position& pos)
{
    if(radius == -1){
        return true;
    }
    
	return ((pos.x >= centerPos.x - radius) && (pos.x <= centerPos.x + radius) &&
			(pos.y >= centerPos.y - radius) && (pos.y <= centerPos.y + radius));
}

// Respawn as in CipSoft's world (docs/reference-74/spawns.md, decided 2026-10-04), with the rules of Nostalrius'
// src/spawn.cpp (a 7.7 server built on CipSoft's files) and tibiantis.info's trivia (7.4):
//  - every slot (one monster of the spawn file) has its own timer: it respawns getRespawnDelay(spawntime) after its
//    monster died, not on a check tick of the whole block;
//  - a player near the spot when it is due (findPlayer) blocks it: the slot waits a whole new delay;
//  - overspawn: a monster that goes more than OVERSPAWN_DISTANCE squares from its spot, or to another floor, frees
//    its slot (it stays in the world until it dies or despawns) and the slot's timer starts.
// RateSpawn (config.lua) divides every delay: 1 = Cip's times; the test server uses it to shorten them.
#define OVERSPAWN_DISTANCE 10
#define RESPAWN_RETRY 10000        // the spot was taken (placeCreature failed): try again after this

void Spawn::startSpawnCheck()
{
	//a monster of this block disappeared (died, despawned): checkSpawn starts its slot's timer
	scheduleCheck(OTSYS_TIME());
}

void Spawn::scheduleCheck(int64_t when)
{
	if(checkSpawnEvent != 0){
		if(checkSpawnTime <= when){
			return;
		}
		stopEvent();
	}

	int64_t delay = when - OTSYS_TIME();
	if(delay < SCHEDULER_MINTICKS){
		delay = SCHEDULER_MINTICKS;
	}
	checkSpawnTime = OTSYS_TIME() + delay;
	checkSpawnEvent = Scheduler::getScheduler().addEvent(createSchedulerTask((uint32_t)delay, boost::bind(&Spawn::checkSpawn, this)));
}

Spawn::Spawn(const Position& _pos, int32_t _radius)
{
	centerPos = _pos;
	radius = _radius;
	checkSpawnEvent = 0;
	checkSpawnTime = 0;
}

Spawn::~Spawn()
{
	Monster* monster;
	for(SpawnedMap::iterator it = spawnedMap.begin(); it != spawnedMap.end(); ++it){
		monster = it->second;
		it->second = NULL;

		monster->setSpawn(NULL);
		if(monster->isRemoved()){
			g_game.FreeThing(monster);
		}
	}

	spawnedMap.clear();
	spawnMap.clear();

	stopEvent();
}

uint32_t Spawn::getRespawnDelay(uint32_t interval)
{
	//Nostalrius Spawn::getInterval: a spawntime over 500 s is shortened only with many players online (not up to
	//200, 200*t/(players/2+100) up to 800, 0.4*t above) and then randomised between half and all of it (a normal
	//distribution around 3/4, cut at both ends); shorter spawntimes are exact
	uint64_t delay = interval;
	if(delay > 500000){
		uint64_t playersOnline = g_game.getPlayersOnline();
		if(playersOnline > 800){
			delay = 2 * delay / 5;
		}
		else if(playersOnline > 200){
			delay = 200 * delay / (playersOnline / 2 + 100);
		}
		delay = random_range((int32_t)(delay / 2), (int32_t)delay, DISTRO_NORMAL);
	}

	int32_t rate = g_config.getNumber(ConfigManager::RATE_SPAWN);
	if(rate > 1){
		delay /= rate;
	}
	if(delay < 1000){
		delay = 1000;
	}
	return (uint32_t)delay;
}

void Spawn::startRespawnTimer(spawnBlock_t& sb, int64_t now)
{
	if(sb.nextSpawn == 0){
		sb.nextSpawn = now + getRespawnDelay(sb.interval);
	}
}

bool Spawn::findPlayer(const Position& pos)
{
	//7.4 (tibiantis.info trivia; Nostalrius uses the multi-floor spectators): a player blocks a respawn from 2 floors
	//above and below underground, and from every floor above (and its own) on the surface
	SpectatorVec list;
	g_game.getSpectators(list, pos, false, true);

	Player* tmpPlayer = NULL;
	for(SpectatorVec::iterator it = list.begin(); it != list.end(); ++it) {
		if(!(tmpPlayer = (*it)->getPlayer()) || tmpPlayer->hasFlag(PlayerFlag_IgnoredByMonsters)){
			continue;
		}

		const Position& playerPos = tmpPlayer->getPosition();
		if(pos.z <= 7){
			if(playerPos.z > pos.z){
				continue;
			}
		}
		else if(std::abs((int32_t)playerPos.z - (int32_t)pos.z) > 2){
			continue;
		}

		return true;
	}

	return false;
}

bool Spawn::isInSpawnZone(const Position& pos)
{
	return Spawns::getInstance()->isInZone(centerPos, radius, pos);
}

static bool isOverspawned(const Position& spot, const Position& pos)
{
	return pos.z != spot.z || std::abs((int32_t)pos.x - (int32_t)spot.x) > OVERSPAWN_DISTANCE ||
		std::abs((int32_t)pos.y - (int32_t)spot.y) > OVERSPAWN_DISTANCE;
}

void Spawn::onMonsterMove(Monster* monster, const Position& newPos)
{
	for(SpawnedMap::iterator it = spawnedMap.begin(); it != spawnedMap.end(); ++it){
		if(it->second != monster){
			continue;
		}

		uint32_t spawnId = it->first;
		if(spawnId == 0){
			return;
		}

		spawnBlock_t& sb = spawnMap[spawnId];
		if(!isOverspawned(sb.pos, newPos)){
			return;
		}

		//the monster is let go (spawn id 0): it is no longer the slot's
		spawnedMap.erase(it);
		spawnedMap.insert(spawned_pair(0, monster));
		startRespawnTimer(sb, OTSYS_TIME());
		scheduleCheck(sb.nextSpawn);
		return;
	}
}

bool Spawn::spawnMonster(uint32_t spawnId, MonsterType* mType, const Position& pos, Direction dir, bool startup /*= false*/)
{
	Monster* monster = Monster::createMonster(mType);
	if(!monster){
		return false;
	}

	if(startup){
		//No need to send out events to the surrounding since there is no one out there to listen!
		if(!g_game.internalPlaceCreature(monster, pos, false, true)){
			delete monster;
			return false;
		}
	}
	else{
		if(!g_game.placeCreature(monster, pos, false, true)){
			delete monster;
			return false;
		}
	}

	monster->setDirection(dir);
	monster->setSpawn(this);
	monster->setMasterPos(pos, radius);
	monster->useThing2();

	spawnedMap.insert(spawned_pair(spawnId, monster));
	spawnMap[spawnId].lastSpawn = OTSYS_TIME();
	spawnMap[spawnId].nextSpawn = 0;
	return true;
}

void Spawn::startup()
{
	int64_t now = OTSYS_TIME();
	for(SpawnMap::iterator it = spawnMap.begin(); it != spawnMap.end(); ++it){
		uint32_t spawnId = it->first;
		spawnBlock_t& sb = it->second;

		if(!spawnMonster(spawnId, sb.mType, sb.pos, sb.direction, true)){
			sb.nextSpawn = now + RESPAWN_RETRY;
			scheduleCheck(sb.nextSpawn);
		}
	}
}

void Spawn::checkSpawn()
{
#ifdef __DEBUG_SPAWN__
	std::cout << "[Notice] Spawn::checkSpawn " << this << std::endl;
#endif
	checkSpawnEvent = 0;
	checkSpawnTime = 0;

	int64_t now = OTSYS_TIME();
	Monster* monster;
	uint32_t spawnId;

	for(SpawnedMap::iterator it = spawnedMap.begin(); it != spawnedMap.end();){
		spawnId = it->first;
		monster = it->second;

		if(monster->isRemoved()) {
			//died or despawned: its slot's timer starts now
			if(spawnId != 0) {
				startRespawnTimer(spawnMap[spawnId], now);
			}

			monster->releaseThing2();
			spawnedMap.erase(it++);
		}
		else if(spawnId != 0 && isOverspawned(spawnMap[spawnId].pos, monster->getPosition())) {
			startRespawnTimer(spawnMap[spawnId], now);
			spawnedMap.insert(spawned_pair(0, monster));
			spawnedMap.erase(it++);
		}
		else{
			++it;
		}
	}

	int64_t nextCheck = 0;
	for(SpawnMap::iterator it = spawnMap.begin(); it != spawnMap.end(); ++it) {
		spawnId = it->first;
		spawnBlock_t& sb = it->second;

		if(spawnedMap.count(spawnId) != 0){
			continue;
		}

		startRespawnTimer(sb, now);
		if(now >= sb.nextSpawn){
			if(findPlayer(sb.pos)){
				//blocked: the slot waits a whole new delay
				sb.nextSpawn = now + getRespawnDelay(sb.interval);
			}
			else if(!spawnMonster(spawnId, sb.mType, sb.pos, sb.direction)){
				sb.nextSpawn = now + RESPAWN_RETRY;
			}
		}

		if(sb.nextSpawn != 0 && (nextCheck == 0 || sb.nextSpawn < nextCheck)){
			nextCheck = sb.nextSpawn;
		}
	}

	if(nextCheck != 0){
		scheduleCheck(nextCheck);
	}
#ifdef __DEBUG_SPAWN__
	else{
		std::cout << "[Notice] Spawn::checkSpawn stopped " << this << std::endl;
	}
#endif
}

bool Spawn::addMonster(const std::string& _name, const Position& _pos, Direction _dir, uint32_t _interval)
{
	MonsterType* mType = g_monsters.getMonsterType(_name);
	if(!mType){
		std::cout << "[Spawn::addMonster] Can not find " << _name << std::endl;
		return false;
	}

	spawnBlock_t sb;
	sb.mType = mType;
	sb.pos = _pos;
	sb.direction = _dir;
	sb.interval = _interval;
	sb.lastSpawn = 0;
	sb.nextSpawn = 0;

	uint32_t spawnId = (int)spawnMap.size() + 1;
	spawnMap[spawnId] = sb;

	return true;
}

void Spawn::removeMonster(Monster* monster)
{
	//convinced (it became a player's summon): the slot is free and its timer starts
	for(SpawnedMap::iterator it = spawnedMap.begin(); it != spawnedMap.end(); ++it){
		if(it->second == monster){
			uint32_t spawnId = it->first;
			monster->releaseThing2();
			spawnedMap.erase(it);

			if(spawnId != 0){
				spawnBlock_t& sb = spawnMap[spawnId];
				startRespawnTimer(sb, OTSYS_TIME());
				scheduleCheck(sb.nextSpawn);
			}
			break;
		}
	}
}

void Spawn::stopEvent()
{
	if(checkSpawnEvent != 0){
		Scheduler::getScheduler().stopEvent(checkSpawnEvent);
		checkSpawnEvent = 0;
		checkSpawnTime = 0;
	}
}
