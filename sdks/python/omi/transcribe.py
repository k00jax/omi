import websockets
import json
import asyncio

async def transcribe(audio_queue, api_key, on_transcript=None, status_callback=None):
    url = "wss://api.deepgram.com/v1/listen?punctuate=true&model=nova&language=en-US&encoding=linear16&sample_rate=16000&channels=1"
    headers = {
        "Authorization": f"Token {api_key}"
    }
    
    while True:
        try:
            if status_callback:
                status_callback("🔄 Connecting to Deepgram...")
            async with websockets.connect(url, additional_headers=headers) as ws:
                print("Connected to Deepgram WebSocket")
                if status_callback:
                    status_callback("🎤 Connected to Deepgram - Ready to transcribe!")

                async def send_audio():
                    audio_bytes_sent = 0
                    while True:
                        try:
                            chunk = await audio_queue.get()
                            await ws.send(chunk)
                            audio_bytes_sent += len(chunk)
                            
                            # Minimal logging - only show major milestones
                            if audio_bytes_sent % 100000 == 0:  # Every ~100KB
                                print(f"🎵 {audio_bytes_sent//1000}KB sent to Deepgram")
                        except Exception as e:
                            print(f"Error sending audio: {e}")
                            break

                async def receive_transcripts():
                    try:
                        async for msg in ws:
                            try:
                                response = json.loads(msg)
                                if "error" in response:
                                    print(f"Deepgram Error: {response['error']}")
                                    continue
                                    
                                # Extract transcript from the response
                                if "channel" in response and "alternatives" in response["channel"]:
                                    transcript = response["channel"]["alternatives"][0].get("transcript", "")
                                    if transcript and transcript.strip():
                                        transcript = transcript.strip()
                                        print("\nTranscript:", transcript)

                                        if on_transcript:
                                            try:
                                                await on_transcript(transcript)
                                            except Exception as e:
                                                print(f"on_transcript error: {e}")

                            except json.JSONDecodeError as e:
                                print(f"Error decoding response: {e}")
                            except Exception as e:
                                print(f"Error processing transcript: {e}")
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection to Deepgram closed")
                    except Exception as e:
                        print(f"Error in receive_transcripts: {e}")

                try:
                    await asyncio.gather(send_audio(), receive_transcripts())
                except Exception as e:
                    print(f"Error in transcribe: {e}")
                    
        except Exception as e:
            print(f"Connection error: {e}")
            if status_callback:
                status_callback(f"⚠️ Deepgram connection lost, retrying...")
            print("Retrying connection in 5 seconds...")
            await asyncio.sleep(5)
