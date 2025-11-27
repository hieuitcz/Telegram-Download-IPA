import os
import sys
import asyncio
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

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
            parts = msg_link.strip('/').split('/')
            entity = None
            msg_id = int(parts[-1]) # Luôn lấy số cuối cùng làm ID tin nhắn mục tiêu
            
            # Case 1: Link có 2 ID số (t.me/xxx/111/222) -> Thường là Channel Post + Comment ID
            if len(parts) >= 5 and parts[-2].isdigit() and parts[-1].isdigit():
                channel_name = parts[-3]
                post_id = int(parts[-2])
                comment_id = int(parts[-1])
                
                print(f"Link dạng Comment. Channel: {channel_name}, Post: {post_id}, Msg: {comment_id}")
                
                # Bước 1: Thử lấy trực tiếp từ Entity (Nếu LKTEAM23 là Group/Supergroup thì sẽ được ngay)
                try:
                    print(f"Thử tải trực tiếp từ {channel_name} với ID {comment_id}...")
                    if channel_name == 'c':
                         real_id = int(f"-100{parts[-3]}") # Private ID
                         entity = await client.get_entity(real_id)
                    else:
                         entity = await client.get_entity(channel_name)
                         
                    message = await client.get_messages(entity, ids=comment_id)
                    if message and message.file:
                        print("=> Thành công! Đây là Supergroup/Group.")
                        await download_file(message)
                        return
                except Exception as e:
                    print(f"=> Không lấy được trực tiếp ({e}). Chuyển sang tìm Discussion Group...")

                # Bước 2: Tìm Discussion Group của Channel
                # Lấy lại entity Channel gốc
                if channel_name == 'c':
                     real_id = int(f"-100{parts[-3]}")
                     channel_entity = await client.get_entity(real_id)
                else:
                     channel_entity = await client.get_entity(channel_name)

                full_channel = await client(functions.channels.GetFullChannelRequest(channel_entity))
                
                if full_channel.full_chat.linked_chat_id:
                    linked_id = full_channel.full_chat.linked_chat_id
                    print(f"Found Linked Group ID: {linked_id}")
                    
                    # Thử lấy entity của Group Linked
                    try:
                        group_entity = await client.get_entity(linked_id)
                    except ValueError:
                        # Nếu không tìm thấy, tức là chưa cache hoặc chưa join
                        print("User chưa thấy Group này bao giờ. Đang thử tìm info...")
                        # Cố gắng resolve qua InputPeer
                        # Lưu ý: Không thể join private group nếu không có invite link.
                        # Nhưng nếu là public group linked với public channel, ta có thể đoán username?
                        # Rất tiếc API không trả về username của linked chat trực tiếp nếu chưa join.
                        
                        # Cách cuối: Dùng GetDiscussionMessage để telethon tự tìm đường
                        print("Đang thử dùng GetDiscussionMessage để định vị...")
                        # post_id là ID của bài viết trong Channel
                        discussion = await client(functions.messages.GetDiscussionMessageRequest(
                            peer=channel_entity,
                            msg_id=post_id
                        ))
                        # discussion.messages chứa các tin nhắn đầu tiên, conversation_peer là group
                        group_entity = discussion.chats[0]
                        print(f"Đã tìm thấy Group: {group_entity.title} (ID: {group_entity.id})")
                        
                    # Tải file từ ID comment trong Group đó
                    print(f"Đang tải tin nhắn {comment_id} từ Group {group_entity.title}...")
                    message = await client.get_messages(group_entity, ids=comment_id)
                    if message and message.file:
                         await download_file(message)
                         return
                    else:
                        print("Không tìm thấy file tại ID này trong Discussion Group.")
                else:
                    print("Channel này KHÔNG có Discussion Group.")

            # Case 2: Link thường (t.me/xxx/123)
            else:
                # Code cũ xử lý link thường...
                pass 
                
        except Exception as e:
            print(f"LỖI: {e}")
            print("-------------------------------------------------")
            print("LỜI KHUYÊN:")
            print("1. Hãy dùng tài khoản Telegram của bạn, bấm vào phần 'Bình luận' (Comment)")
            print("   của bài viết đó trên Channel để join vào nhóm chat trước.")
            print("2. Sau khi join xong, chạy lại Action này sẽ thành công.")
            print("-------------------------------------------------")
            sys.exit(1)

async def download_file(message):
    print(f"Found file: {message.file.name}")
    print("Downloading...")
    def progress_callback(current, total):
        print(f"Downloaded: {current * 100 / total:.1f}%", end='\r')
    
    path = await message.download_media(progress_callback=progress_callback)
    print(f"\nDownloaded to: {path}")
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print(f"file_path={path}", file=fh)

if __name__ == '__main__':
    asyncio.run(main())
