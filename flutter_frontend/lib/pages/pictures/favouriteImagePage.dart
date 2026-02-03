import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/pictures/requests/favouriteImageRequest.dart';

class FavouriteImagePage extends StatelessWidget {
  final String pictureId;

  const FavouriteImagePage({super.key, required this.pictureId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Favourite Images')),
      body: Center(child: FavouriteImageRequest(pictureId: pictureId)),
    );
  }
}
