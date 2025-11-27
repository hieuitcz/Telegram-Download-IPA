import os
import sys
import asyncio
from telethon import TelegramClient
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
        
        try:
            entity = None
            msg_id = 0
            
            # Phân tích link
            parts = msg_link.strip('/').split('/')
            
            # LOGIC MỚI: Xử lý link Comment (Channel + Post ID + Comment ID)
            # Link dạng: t.me/ChannelName/1234/5678 (Post 1234, Comment 5678)
            if len(parts) >= 5 and parts[-2].isdigit() and parts[-1].isdigit():
                # Đây là link tới COMMENT
                channel_identifier = parts[-3] # Channel Username hoặc c/ID
                post_id = int(parts[-2]) # ID bài post gốc
                comment_id = int(parts[-1]) # ID của comment chứa file
                
                print(f"Detected Comment Link. Channel: {channel_identifier}, Post: {post_id}, Comment: {comment_id}")
                
                # Lấy entity của Channel gốc trước
                if channel_identifier == 'c':
                    # Private channel: t.me/c/123456789/POST/COMMENT
                    channel_id = int(f"-100{parts[-3]}") # Lấy lại index đúng
                    entity = await client.get_entity(channel_id)
                else:
                    # Public channel
                    entity = await client.get_entity(channel_identifier)
                
                # Telethon không lấy trực tiếp Comment bằng ID như tin nhắn thường được
                # Ta phải lấy tin nhắn gốc, sau đó tìm trong các reply
                # Hoặc: Comment thực chất nằm trong "Linked Chat" (Discussion Group)
                
                # Cách 1: Lấy trực tiếp từ Discussion Group (nhanh hơn nếu User đã join Group)
                # Nhưng để an toàn, ta dùng get_messages với tham số reply_to nếu cần, 
                # hoặc đơn giản nhất: Với link t.me/xxx/POST/COMMENT, thì COMMENT_ID 
                # chính là ID tin nhắn trong Discussion Group.
                
                # Ta cần tìm ID của Discussion Group liên kết
                full_channel = await client(functions.channels.GetFullChannelRequest(entity))
                if full_channel.full_chat.linked_chat_id:
                    discussion_group_id = full_channel.full_chat.linked_chat_id
                    print(f"Found Linked Discussion Group ID: {discussion_group_id}")
                    entity = await client.get_entity(discussion_group_id)
                    msg_id = comment_id
                else:
                    print("Channel này không có Discussion Group hoặc User chưa join.")
                    sys.exit(1)
            
            # Case cũ: Link Channel thường hoặc Private Group
            elif '/c/' in msg_link: # Private Link
                channel_id_str = parts[-2]
                msg_id = int(parts[-1])
                real_id = int(f"-100{channel_id_str}")
                entity = await client.get_entity(real_id)
                
            else: # Public Link thường (t.me/user/123)
                username = parts[-2]
                msg_id = int(parts[-1])
                entity = await client.get_entity(username)

            # Tải tin nhắn
            print(f"Fetching message ID: {msg_id} from {entity.title if hasattr(entity, 'title') else 'Entity'}")
            message = await client.get_messages(entity, ids=msg_id)
            
            if message and message.media:
                print(f"Found media: {message.file.name if message.file else 'Unknown'}")
                
                # Filter: Chỉ tải IPA nếu cần (tùy chọn)
                # if not message.file.name.endswith('.ipa'): ...
                
                print("Downloading...")
                def progress_callback(current, total):
                    print(f"Downloaded: {current * 100 / total:.1f}%", end='\r')

                path = await message.download_media(progress_callback=progress_callback)
                print(f"\nDownloaded to: {path}")
                
                if 'GITHUB_OUTPUT' in os.environ:
                    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
                        print(f"file_path={path}", file=fh)
            else:
                print("No media found in this message.")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
from telethon import functions # Import thêm functions

if __name__ == '__main__':
    asyncio.run(main())
