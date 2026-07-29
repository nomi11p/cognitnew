import 'package:flutter/material.dart';

import '../widgets/suggetion_chips.dart';
import '../widgets/app_drawer.dart';
import '../widgets/chat_area.dart';
import '../widgets/chat_input.dart';
import '../models/chat_message.dart';
import '../services/api_service.dart';


class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}


class _HomeScreenState extends State<HomeScreen> {

  final List<ChatMessage> messages = [];

  bool isTyping = false;

  String currentMood = "Normal";


  Future<void> sendMessage(String text) async {

    setState(() {

      messages.add(
        ChatMessage(
          text: text,
          isUser: true,
        ),
      );

      isTyping = true;

    });


   final reply = await ApiService.sendMessage(
  text,
  currentMood.toLowerCase(),
);


    setState(() {

      isTyping = false;


      messages.add(
        ChatMessage(
          text: reply,
          isUser: false,
        ),
      );

    });

  }



  @override
  Widget build(BuildContext context) {

    return Scaffold(

      appBar: AppBar(
        title: const Text("Cognit AI"),
        centerTitle: true,
      ),


      drawer: const AppDrawer(),


      body: Column(

        children: [

          Expanded(

            child: ChatArea(
              messages: messages,
              isTyping: isTyping,
            ),

          ),


          if (messages.isEmpty)

            SuggestionChips(
              onSuggestionTap: sendMessage,
            ),


          ChatInput(
            onSend: sendMessage,
          ),

        ],

      ),

    );

  }
}