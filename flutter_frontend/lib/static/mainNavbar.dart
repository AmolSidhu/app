import 'package:flutter/material.dart';

// General Pages
import 'package:flutter_frontend/pages/general/homePage.dart';
import 'package:flutter_frontend/pages/general/aboutPage.dart';
import 'package:flutter_frontend/pages/general/profilePage.dart';

// Video Pages
import 'package:flutter_frontend/pages/videos/videoPage.dart';
import 'package:flutter_frontend/pages/videos/makeVideoRequestPage.dart';
import 'package:flutter_frontend/pages/videos/videoCustomListPage.dart';
import 'package:flutter_frontend/pages/videos/videoFavouritePage.dart';
import 'package:flutter_frontend/pages/videos/videoUploadPage.dart';

// Picture Pages
import 'package:flutter_frontend/pages/pictures/customImageAlbumsPage.dart';
import 'package:flutter_frontend/pages/pictures/defaultImageAlbumPage.dart';
import 'package:flutter_frontend/pages/pictures/favouriteImagePage.dart';

// Music Pages
import 'package:flutter_frontend/pages/music/viewAllCustomMusicPlaylistsPage.dart';
import 'package:flutter_frontend/pages/music/viewAllArtistsPage.dart';
import 'package:flutter_frontend/pages/music/viewAllMusicAlbumsPage.dart';

// Youtube Pages
import 'package:flutter_frontend/pages/youtube/myYoutubeListsPage.dart';

// Analytics Pages
import 'package:flutter_frontend/pages/analytics/createDashboardPage.dart';
import 'package:flutter_frontend/pages/analytics/myDashboardsPage.dart';
import 'package:flutter_frontend/pages/analytics/uploadDataSourcePage.dart';

// MTG Pages
import 'package:flutter_frontend/pages/mtg/uploadScraperPage.dart';
import 'package:flutter_frontend/pages/mtg/viewScraperPage.dart';
import 'package:flutter_frontend/pages/mtg/viewAllMagicCardsPage.dart';

// File Pages
import 'package:flutter_frontend/pages/files/myUploadFilePage.dart';
import 'package:flutter_frontend/pages/files/uploadShareFilePage.dart';

// Article Pages
import 'package:flutter_frontend/pages/articles/myArticlesPage.dart';
import 'package:flutter_frontend/pages/articles/uploadArticlesPage.dart';

// Management Pages
import 'package:flutter_frontend/pages/management/accountDetailPage.dart';
import 'package:flutter_frontend/pages/management/myVideoUploadsPage.dart';
import 'package:flutter_frontend/pages/management/viewAllPictureUploadsPage.dart';
import 'package:flutter_frontend/pages/management/viewAllVideoUploadsPage.dart';
import 'package:flutter_frontend/pages/management/viewMyVideoRequestsPage.dart';

// Admin Pages
import 'package:flutter_frontend/pages/admin/adminDataPage.dart';
import 'package:flutter_frontend/pages/admin/videoRequestApprovalPage.dart';
import 'package:flutter_frontend/pages/admin/adminFileUploadPage.dart';

// Logout
import 'package:flutter_frontend/assets/auth/requests/logoutRequest.dart';

// Login Navbar
import 'package:flutter_frontend/static/loginNavbar.dart';

// Server Data Popup
import 'package:flutter_frontend/assets/general/popups/serverMetaDataPopup.dart';

class MainNavbar extends StatefulWidget {
  final bool isAdmin;

  static final GlobalKey<NavigatorState> rootNav = GlobalKey<NavigatorState>();

  static final GlobalKey<NavigatorState> contentNav =
      GlobalKey<NavigatorState>();

  const MainNavbar({Key? key, required this.isAdmin}) : super(key: key);

  @override
  _MainNavbarState createState() => _MainNavbarState();
}

class _MainNavbarState extends State<MainNavbar> {
  bool isExpanded = true;
  bool showServerMeta = false;

  String selectedPageKey = 'HomePage';
  static String pictureId = '';

  late final Map<String, List<Map<String, dynamic>>> sections;

  @override
  void initState() {
    super.initState();
    sections = _buildSections();
  }

  Map<String, List<Map<String, dynamic>>> _buildSections() {
    final map = <String, List<Map<String, dynamic>>>{
      'General Pages': [
        {'title': 'Home', 'pageKey': 'HomePage', 'page': HomePage()},
        {'title': 'About', 'pageKey': 'AboutPage', 'page': AboutPage()},
        {'title': 'Profile', 'pageKey': 'ProfilePage', 'page': ProfilePage()},
      ],

      'Video Pages': [
        {'title': 'Videos', 'pageKey': 'VideoPage', 'page': VideoPage()},
        {
          'title': 'Make Video Request',
          'pageKey': 'MakeVideoRequestPage',
          'page': MakeVideoRequestPage(),
        },
        {
          'title': 'Custom Video List',
          'pageKey': 'VideoCustomListPage',
          'page': VideoCustomListPage(),
        },
        {
          'title': 'Favourite Videos',
          'pageKey': 'VideoFavouritePage',
          'page': VideoFavouritePage(),
        },
        {
          'title': 'Upload Video',
          'pageKey': 'VideoUploadPage',
          'page': VideoUploadPage(),
        },
      ],

      'Picture Pages': [
        {
          'title': 'Custom Image Albums',
          'pageKey': 'CustomImageAlbumsPage',
          'page': CustomImageAlbumsPage(),
        },
        {
          'title': 'Default Image Album',
          'pageKey': 'DefaultImageAlbumPage',
          'page': DefaultImageAlbumPage(),
        },
        {
          'title': 'Favourite Images',
          'pageKey': 'FavouriteImagePage',
          'page': FavouriteImagePage(pictureId: pictureId),
        },
      ],

      'Music Pages': [
        {
          'title': 'Custom Playlist',
          'pageKey': 'CustomPlaylistPage',
          'page': ViewAllCustomMusicPlaylistPage(),
        },
        {
          'title': 'View All Artists',
          'pageKey': 'ViewAllArtistsPage',
          'page': ViewAllArtistsPage(),
        },
        {
          'title': 'View All Music Albums',
          'pageKey': 'ViewAllMusicAlbumsPage',
          'page': ViewAllMusicAlbumsPage(),
        },
      ],

      'Youtube Pages': [
        {
          'title': 'My Youtube Lists',
          'pageKey': 'MyYoutubeListsPage',
          'page': MyYoutubeListsPage(),
        },
      ],

      'Analytics Pages': [
        {
          'title': 'Create Dashboard',
          'pageKey': 'CreateDashboardPage',
          'page': CreateDashboardPage(),
        },
        {
          'title': 'My Dashboards',
          'pageKey': 'MyDashboardsPage',
          'page': MyDashboardsPage(),
        },
        {
          'title': 'Upload Data Source',
          'pageKey': 'UploadDataSourcePage',
          'page': UploadDataSourcePage(),
        },
      ],

      'MTG Pages': [
        {
          'title': 'Upload Scraper',
          'pageKey': 'UploadScraperPage',
          'page': UploadScraperPage(),
        },
        {
          'title': 'View Scraper',
          'pageKey': 'ViewScraperPage',
          'page': ViewScraperPage(),
        },
        {
          'title': 'View All Magic Cards',
          'pageKey': 'ViewAllMagicCardsPage',
          'page': ViewAllMagicCardsPage(),
        },
      ],

      'File Pages': [
        {
          'title': 'My Upload File',
          'pageKey': 'MyUploadFilePage',
          'page': MyUploadFilePage(),
        },
        {
          'title': 'Upload Share File',
          'pageKey': 'UploadShareFilePage',
          'page': UploadShareFilePage(),
        },
      ],

      'Article Pages': [
        {
          'title': 'Upload Articles',
          'pageKey': 'UploadArticlesPage',
          'page': UploadArticlesPage(),
        },
        {
          'title': 'My Articles',
          'pageKey': 'MyArticlesPage',
          'page': MyArticlesPage(),
        },
      ],

      'Management Pages': [
        {
          'title': 'Account Detail',
          'pageKey': 'AccountDetailPage',
          'page': AccountDetailPage(),
        },
        {
          'title': 'My Video Uploads',
          'pageKey': 'MyVideoUploadsPage',
          'page': MyVideoUploadsPage(),
        },
        {
          'title': 'View All Picture Uploads',
          'pageKey': 'ViewAllPictureUploadsPage',
          'page': ViewAllPictureUploadsPage(),
        },
        {
          'title': 'View All Video Uploads',
          'pageKey': 'ViewAllVideoUploadsPage',
          'page': ViewAllVideoUploadsPage(),
        },
        {
          'title': 'View My Video Requests',
          'pageKey': 'ViewMyVideoRequestsPage',
          'page': ViewMyVideoRequestsPage(),
        },
      ],
    };

    if (widget.isAdmin) {
      map['Admin Pages'] = [
        {
          'title': 'User Stats',
          'pageKey': 'adminDataPage',
          'page': AdminDataPage(),
          'adminOnly': true,
        },
        {
          'title': 'Review Video Requests',
          'pageKey': 'videoRequestApprovalPage',
          'page': VideoRequestApprovalPage(),
          'adminOnly': true,
        },
        {
          'title': 'Admin File Upload',
          'pageKey': 'adminFileUploadPage',
          'page': AdminFileUploadPage(),
          'adminOnly': true,
        },
      ];
    }

    return map;
  }

  Widget _resolvePage() {
    final allPages = sections.values.expand((e) => e);

    final page = allPages.firstWhere(
      (item) => item['pageKey'] == selectedPageKey,
      orElse: () => {},
    );

    if (page.isEmpty) {
      return const Center(child: Text('Page not found'));
    }

    if (page['adminOnly'] == true && !widget.isAdmin) {
      return const Center(child: Text('Access denied'));
    }

    return page['page'] as Widget;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          Row(
            children: [
              // Sidebar
              AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                width: isExpanded ? 250 : 70,
                color: Colors.blueGrey.shade900,
                child: Column(
                  children: [
                    Align(
                      alignment: Alignment.centerRight,
                      child: IconButton(
                        icon: Icon(
                          isExpanded ? Icons.arrow_left : Icons.arrow_right,
                          color: Colors.white,
                        ),
                        onPressed: () =>
                            setState(() => isExpanded = !isExpanded),
                      ),
                    ),

                    Expanded(
                      child: ListView(
                        padding: EdgeInsets.zero,
                        children: [
                          if (isExpanded)
                            const DrawerHeader(
                              decoration: BoxDecoration(color: Colors.blue),
                              child: Text(
                                'Main Navbar',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 24,
                                ),
                              ),
                            ),

                          ...sections.entries.map((entry) {
                            return ExpansionTile(
                              leading: const Icon(
                                Icons.folder,
                                color: Colors.white,
                              ),
                              title: isExpanded
                                  ? Text(
                                      entry.key,
                                      style: const TextStyle(
                                        color: Colors.white,
                                      ),
                                    )
                                  : const SizedBox.shrink(),
                              collapsedBackgroundColor:
                                  Colors.blueGrey.shade800,
                              children: isExpanded
                                  ? entry.value.map((item) {
                                      return ListTile(
                                        title: Text(
                                          item['title'],
                                          style: const TextStyle(
                                            color: Colors.white,
                                          ),
                                        ),
                                        onTap: () {
                                          setState(
                                            () => selectedPageKey =
                                                item['pageKey'],
                                          );

                                          MainNavbar.contentNav.currentState!
                                              .pushReplacement(
                                                MaterialPageRoute(
                                                  builder: (_) => item['page'],
                                                ),
                                              );
                                        },
                                      );
                                    }).toList()
                                  : [],
                            );
                          }).toList(),
                        ],
                      ),
                    ),

                    ListTile(
                      leading: const Icon(
                        Icons.info_outline,
                        color: Colors.white,
                      ),
                      title: isExpanded
                          ? const Text(
                              'Application Info',
                              style: TextStyle(color: Colors.white),
                            )
                          : null,
                      onTap: () => setState(() => showServerMeta = true),
                    ),

                    ListTile(
                      leading: const Icon(Icons.logout, color: Colors.white),
                      title: isExpanded
                          ? const Text(
                              'Logout',
                              style: TextStyle(color: Colors.white),
                            )
                          : null,
                      onTap: () async {
                        await logoutRequest();
                        MainNavbar.rootNav.currentState!.pushAndRemoveUntil(
                          MaterialPageRoute(
                            builder: (_) => const LoginNavbar(),
                          ),
                          (_) => false,
                        );
                      },
                    ),
                  ],
                ),
              ),

              Expanded(
                child: Navigator(
                  key: MainNavbar.contentNav,
                  onGenerateRoute: (settings) {
                    return MaterialPageRoute(builder: (_) => _resolvePage());
                  },
                ),
              ),
            ],
          ),

          if (showServerMeta)
            Positioned.fill(
              child: Container(
                color: Colors.black54,
                child: ServerMetaDataPopup(
                  onClose: () => setState(() => showServerMeta = false),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
