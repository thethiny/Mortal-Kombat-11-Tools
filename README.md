# A collection of MK11 tools I've written throught the years

## `x-ag-binary`
Data format of Warner Bros Games' API Content Data.

## mk11-extractors
Used to extract the databases of MK11's databases. I don't remember the difference between this and the extractor below. Refer to unlocker to see which it uses.
Can also extract COALESCED files.
Also contains code to parse MK11's items and convert the database to json. Basically this deals with extracting all equipment/items/unlockables in the game.

## mk11-api
- Contains my attempts at an MK11 private server.
- Contains code to create an MITM MK11 server that allows you to create a private server later (requires MK11).
- Contains code to convert to x-ag-binary from json.
- Contains a bunch of API examples

## mk11-formats
Contains a bunch of 010 templates to help you read MK11 files, and a bunch of ReClass files that help you read MK11 Classes in memory.

## ASIMK11
A bunch of mods for MK11 and enables the usage of the Unlocker for the steam version of the game.

https://github.com/thethiny/ASIMK11

## MK11 Unlocker
A Mortal Kombat 11 tool that allows you to unlock any item in the game.
Compatible with Steam and Xbox.

https://github.com/thethiny/MK11-Unlocker * Private

## MK11 Database Extractor
Tools that allow you to extract the contents of MK11's Database type.
Found in files such as MK11ItemDatabase.xxx

https://github.com/thethiny/MK11-Database-Extractor

## MK11 Package Extractor
Allows you to extract & repack MK11 .xxx files

https://github.com/thethiny/MK11-PackageExtractor

Repack was never completed so manual injection of skins required.
Switch to `Repack` branch.


## MK11 Daily Tracker
A twitter bot that connects to the MK11 API and tweets the daily store.
Also tweets secret tower timings.

https://github.com/thethiny/MK11DailyTracker
*Private

## MK11 VR Hasher
### Update 2025
VR2 Hasher is now available, uses MT19937 as seed, and a custom FNV1-a key that is player dependant.
https://github.com/thethiny/MK11-VR2-Hasher
Hashes unlock payload using the first VR hash, dubbed `vr` hash. MK11 later introduced `vr2` hash that uses async communication, which requires ASIMK11. How the hash is calculated for `vr2` is unknown, however the hash is done on the item's `SlugId` + `ts` (time string) using the user's personal key, generated in-game. The key is constant and doesn't change across runs.

`vr2` input is in the format: `{tsString}:{slugId}`

`ts` is in the format: `{day}_{hour}:{minute}:{sec}_ID`. `ts` Can be replaced with other value as long as it's passed in the payload and hashed with it.

`vr2` is an 8-byte value, where only the least significat 4 bytes are used. For example, `0x1AABBCCDD` becomes `0xAABBCCDD`.


https://github.com/thethiny/MK11-VR-Hasher
