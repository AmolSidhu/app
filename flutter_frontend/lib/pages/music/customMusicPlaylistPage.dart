import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/music/requests/customMusicPlaylistRequest.dart';
import 'package:flutter_frontend/assets/music/requests/customMusicPlayerRequest.dart';

class CustomMusicPlaylistPage extends StatefulWidget {
  @override
  State<CustomMusicPlaylistPage> createState() =>
      _CustomMusicPlaylistPageState();
}

class _CustomMusicPlaylistPageState extends State<CustomMusicPlaylistPage> {
  int _reloadCounter = 0;

  void _onTrackSelected() {
    setState(() {
      _reloadCounter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Custom Music Playlist Page')),
      body: Column(
        children: [
          Expanded(
            child: CustomMusicPlaylistRequest(
              onTrackSelected: _onTrackSelected,
            ),
          ),
          Divider(height: 1),
          SizedBox(
            child: CustomMusicPlayerRequest(reloadTrigger: _reloadCounter),
          ),
        ],
      ),
    );
  }
}
