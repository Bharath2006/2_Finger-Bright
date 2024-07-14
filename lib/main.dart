import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hand Brightness Control',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: BrightnessControlPage(),
    );
  }
}

class BrightnessControlPage extends StatefulWidget {
  @override
  _BrightnessControlPageState createState() => _BrightnessControlPageState();
}

class _BrightnessControlPageState extends State<BrightnessControlPage> {
  // Replace with your machine's IP address
  final String startUrl = 'http://192.168.45.39:5000/adjust-brightness';
  final String stopUrl = 'http://192.168.45.39:5000/stop-brightness';
  bool isAdjusting = false;

  void adjustBrightness() async {
    try {
      final response = await http.get(Uri.parse(startUrl));
      if (response.statusCode == 200) {
        print('Brightness adjustment started successfully');
        setState(() {
          isAdjusting = true;
        });
      } else {
        print('Failed to start brightness adjustment');
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  void stopBrightnessAdjustment() async {
    try {
      final response = await http.get(Uri.parse(stopUrl));
      if (response.statusCode == 200) {
        print('Brightness adjustment stopped successfully');
        setState(() {
          isAdjusting = false;
        });
      } else {
        print('Failed to stop brightness adjustment');
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Hand Brightness Control'),
      ),
      body: Center(
        child: ElevatedButton(
          onPressed: isAdjusting ? stopBrightnessAdjustment : adjustBrightness,
          child: Text(
              isAdjusting ? 'Stop Adjusting Brightness' : 'Adjust Brightness'),
        ),
      ),
    );
  }
}
