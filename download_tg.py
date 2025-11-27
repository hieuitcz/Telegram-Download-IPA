import os
import sys
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

# Lấy biến môi trường
api_id = int(os.environ['TG_API_ID'])
api_hash = os.environ['TG_API_HASH']
session_string = os.environ['TG_SESSION_STRING']
# Link tin nhắn dạng: https://t.me/channel_username/123 hoặc https://t.me/c/xxxxxx/123
msg_link = sys.argv[1] 

async def main():
    print(f"Connecting to Telegram...")
    async with TelegramClient(StringSession(session_string), api_id, api_hash) as client:
        print(f"Processing link: {msg_link}")
        
        try:
            # Lấy entity và message ID từ link
            if '/c/' in msg_link: # Private group/channel
                # Cần xử lý logic lấy ID channel private (thường phức tạp hơn chút, nên join channel trước)
                # Ví dụ đơn giản cho public/username link:
                entity_str = msg_link.split('/')[-2]
                msg_id = int(msg_link.split('/')[-1])
                entity = await client.get_entity(int(f"-100{entity_str}") if entity_str.isdigit() else entity_str)
            else: # Public channel
                parts = msg_link.split('/')
                entity = await client.get_entity(parts[-2])
                msg_id = int(parts[-1])

            message = await client.get_messages(entity, ids=msg_id)
            
            if message and message.media:
                print("Found media. Downloading...")
                path = await message.download_media()
                print(f"Downloaded to: {path}")
                # Ghi tên file ra output để step sau dùng
                with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
                    print(f"file_path={path}", file=fh)
            else:
                print("No media found in this message.")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
