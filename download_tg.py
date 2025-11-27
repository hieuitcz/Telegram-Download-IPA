import os
import sys
import asyncio
from telethon import TelegramClient, utils
from telethon.sessions import StringSession
from telethon.tl.types import PeerChannel

# Lấy biến môi trường
api_id = int(os.environ['TG_API_ID'])
api_hash = os.environ['TG_API_HASH']
session_string = os.environ['TG_SESSION_STRING']
msg_link = sys.argv[1] 

async def main():
    print(f"Connecting to Telegram...")
    async with TelegramClient(StringSession(session_string), api_id, api_hash) as client:
        print(f"Processing link: {msg_link}")
        
        entity = None
        msg_id = 0

        try:
            # Case 1: Private Link (t.me/c/1234567890/123)
            if '/c/' in msg_link:
                parts = msg_link.split('/')
                # ID channel private trong link thường thiếu prefix -100
                # Ví dụ: t.me/c/151645/160297 -> Channel ID: 151645 -> Real ID: -100151645
                channel_id_str = parts[-2]
                msg_id = int(parts[-1])
                
                # Thử convert sang ID chuẩn của Telethon (-100...)
                real_id = int(f"-100{channel_id_str}")
                print(f"Trying to fetch entity with ID: {real_id}")
                
                try:
                    entity = await client.get_entity(real_id)
                except ValueError:
                    # Nếu không tìm thấy, có thể do chưa join hoặc ID sai format
                    # Fallback: Thử dùng PeerChannel trực tiếp (đôi khi cần thiết)
                    print("Entity not found in cache. Trying PeerChannel construct...")
                    entity = PeerChannel(real_id)

            # Case 2: Public Link (t.me/username/123)
            else:
                parts = msg_link.split('/')
                username = parts[-2]
                msg_id = int(parts[-1])
                print(f"Fetching public entity: {username}")
                entity = await client.get_entity(username)

            # Tải tin nhắn
            print(f"Fetching message ID: {msg_id}")
            message = await client.get_messages(entity, ids=msg_id)
            
            if message and message.media:
                print(f"Found media: {message.file.name if message.file else 'Unknown'}")
                print("Downloading...")
                
                # Sử dụng thanh tiến trình đơn giản
                def progress_callback(current, total):
                    print(f"Downloaded: {current * 100 / total:.1f}%", end='\r')

                path = await message.download_media(progress_callback=progress_callback)
                print(f"\nDownloaded to: {path}")
                
                # Ghi output cho GitHub Action
                if 'GITHUB_OUTPUT' in os.environ:
                    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
                        print(f"file_path={path}", file=fh)
            else:
                print("No media found in this message or message access restricted.")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error details: {e}")
            print("\nLƯU Ý QUAN TRỌNG:")
            print("1. Đảm bảo tài khoản Telegram (Userbot) ĐÃ JOIN vào group/channel chứa file.")
            print("2. Nếu là Private Group, bạn bắt buộc phải join trước.")
            sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
