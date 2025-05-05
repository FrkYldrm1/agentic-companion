import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<Map<String, String>> _messages = [];
  final TextEditingController _controller = TextEditingController();

  late stt.SpeechToText _speech;
  late FlutterTts _tts;
  bool _isListening = false;
  bool _lastInputWasVoice = false;
  String? _lastConversationId;

  @override
  void initState() {
    super.initState();
    _speech = stt.SpeechToText();
    _tts = FlutterTts();
    _initTts();
  }

  Future<void> _initTts() async {
    await _tts.setLanguage("en-US");
    await _tts.setPitch(1.0);
    await _tts.setSpeechRate(0.5);
  }

  void _toggleListening() async {
    if (!_isListening) {
      bool available = await _speech.initialize(
        onStatus: (val) {
          if (val == 'done') {
            setState(() => _isListening = false);
          }
        },
        onError: (val) {
          setState(() => _isListening = false);
        },
      );
      if (available) {
        setState(() => _isListening = true);
        _speech.listen(
          onResult: (val) {
            if (val.finalResult) {
              _lastInputWasVoice = true;
              _sendMessage(inputText: val.recognizedWords);
            }
          },
        );
      }
    } else {
      setState(() => _isListening = false);
      _speech.stop();
    }
  }

  void _listenToSupervisorResponse(String conversationId) {
    final channel = WebSocketChannel.connect(
      Uri.parse('ws://192.168.50.219:8000/ws/$conversationId'),
    );

    channel.stream.listen((finalReply) async {
      print("🎯 WebSocket reply: $finalReply");
      setState(() {
        _messages.add({'sender': 'supervisor', 'text': finalReply});
      });
      await _tts.speak(finalReply);
      channel.sink.close();
    }, onError: (error) {
      print("❌ WebSocket error: $error");
    });
  }

  Future<String> fetchAgentReply(
      String userMessage, String conversationId) async {
    final url = Uri.parse('http://192.168.50.219:8000/agent/chat');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'message': userMessage,
          'conversation_id': conversationId,
        }),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['reply'];
      } else {
        return 'Error: ${response.statusCode}';
      }
    } catch (e) {
      return 'Connection error: $e';
    }
  }

  void _sendMessage({String? inputText}) async {
    final text = inputText ?? _controller.text.trim();
    if (text.isEmpty) return;

    final conversationId = DateTime.now().millisecondsSinceEpoch.toString();
    _lastConversationId = conversationId;
    print("📡 Using conversation ID: $conversationId");
    _listenToSupervisorResponse(conversationId);

    setState(() {
      _messages.add({'sender': 'user', 'text': text});
      _messages.add({'sender': 'agent', 'text': '...'});
    });
    _controller.clear();

    final reply = await fetchAgentReply(text, conversationId);

    setState(() {
      _messages[_messages.length - 1] = {'sender': 'agent', 'text': reply};
    });

    if (_lastInputWasVoice) {
      await _tts.speak(reply);
      _lastInputWasVoice = false;
    }
  }

  Widget _buildMessage(Map<String, String> message) {
    final isUser = message['sender'] == 'user';
    final isSupervisor = message['sender'] == 'supervisor';
    final bgColor = isUser
        ? Colors.teal[100]
        : isSupervisor
            ? Colors.orange[100]
            : Colors.grey[200];

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        padding: const EdgeInsets.all(16),
        constraints: const BoxConstraints(maxWidth: 300),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          message['text'] ?? '',
          style: const TextStyle(fontSize: 18),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Agentic Companion Chat'),
        centerTitle: true,
        backgroundColor: Colors.teal.shade600,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: _messages.length,
              itemBuilder: (_, i) => _buildMessage(_messages[i]),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            color: Colors.grey.shade100,
            child: Row(
              children: [
                IconButton(
                  icon: Icon(_isListening ? Icons.mic : Icons.mic_none,
                      size: 28, color: Colors.teal),
                  onPressed: _toggleListening,
                ),
                Expanded(
                  child: TextField(
                    controller: _controller,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _sendMessage(),
                    decoration: InputDecoration(
                      hintText: 'Type or speak your message...',
                      contentPadding:
                          const EdgeInsets.symmetric(horizontal: 16),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    style: const TextStyle(fontSize: 18),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.send, size: 28, color: Colors.teal),
                  onPressed: _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
