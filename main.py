#hello there (:
import asyncio
from detector.old import OldDetector
from detector.new import NewDetector
from scraper.manager import run_scraper

async def main():
    old = OldDetector()
    new = NewDetector()

    loop = asyncio.get_event_loop()
    old_task = loop.run_in_executor(None, old.run)
    new_task = asyncio.create_task(new.run_periodically(interval=150))
    scraper_task = asyncio.create_task(run_scraper(interval=120, batch_size=35))

    await asyncio.gather(old_task, new_task, scraper_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 The program was terminated by server command.")
