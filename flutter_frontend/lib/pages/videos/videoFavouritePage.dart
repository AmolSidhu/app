import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/videos/requests/videoFavouriteRequest.dart';

class VideoFavouritePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Favourite Videos')),
      body: Center(child: VideoFavouriteRequest()),
    );
  }
}
