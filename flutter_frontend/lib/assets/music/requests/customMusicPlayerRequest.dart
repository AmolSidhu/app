import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:just_audio/just_audio.dart';
import 'package:flutter_frontend/static/constants.dart';

class CustomMusicPlayerRequest extends StatefulWidget {
  final int reloadTrigger;

  const CustomMusicPlayerRequest({Key? key, required this.reloadTrigger})
    : super(key: key);

  @override
  State<CustomMusicPlayerRequest> createState() =>
      _CustomMusicPlayerRequestState();
}

class _CustomMusicPlayerRequestState extends State<CustomMusicPlayerRequest> {
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  final AudioPlayer _audioPlayer = AudioPlayer();

  Uint8List? _thumbnailBytes;

  String? _playlistSerial;
  String? _customPlaylistTrackSerial;
  String? _trackSerial;

  bool _isPlaying = false;
  bool _shuffleEnabled = false;
  bool _orderEnabled = false;

  Duration _currentPosition = Duration.zero;
  Duration _totalDuration = Duration.zero;

  bool _isUserSeeking = false;

  Duration _resumePosition = Duration.zero;

  bool _hasStartedStreaming = false;

  StreamSubscription<Duration>? _positionSub;
  StreamSubscription<Duration?>? _durationSub;
  StreamSubscription<PlayerState>? _playerStateSub;

  bool _isSavingHistory = false;

  Timer? _historyTimer;

  @override
  void initState() {
    super.initState();
    _initializePlayer();

    _historyTimer = Timer.periodic(const Duration(seconds: 5), (timer) async {
      if (!mounted) return;
      if (_audioPlayer.playing) {
        await _saveHistoryPosition();
      }
    });
  }

  @override
  void didUpdateWidget(CustomMusicPlayerRequest oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (oldWidget.reloadTrigger != widget.reloadTrigger) {
      _handleReloadAndPlayNewTrack();
    }
  }

  Future<void> _handleReloadAndPlayNewTrack() async {
    await _audioPlayer.stop();
    _isPlaying = false;
    _hasStartedStreaming = false;

    await _initializePlayer();

    if (_trackSerial != null && _customPlaylistTrackSerial != null) {
      await _togglePlay();
    }
  }

  @override
  void dispose() {
    _historyTimer?.cancel();

    _saveHistoryPosition();

    _positionSub?.cancel();
    _durationSub?.cancel();
    _playerStateSub?.cancel();
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> _initializePlayer() async {
    final token = await _secureStorage.read(key: 'token');
    _playlistSerial = await _secureStorage.read(
      key: 'customMusicPlaylistSerial',
    );

    _hasStartedStreaming = false;

    await _fetchPlayerSettings(token);
    await _fetchCurrentlyPlayingTrack(token);
    await _fetchThumbnail(token);

    _listenToPlayer();
  }

  Future<void> _fetchPlayerSettings(String? token) async {
    final response = await http.get(
      Uri.parse('$server/get/custom_music_player_settings/'),
      headers: {
        'Authorization': token ?? '',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body)['data'];

      setState(() {
        _shuffleEnabled = data['shuffle_playback'] ?? false;
        _orderEnabled = data['order_playback'] ?? false;
      });
    }
  }

  Future<void> _updatePlayerSettings({bool? shuffle, bool? order}) async {
    final token = await _secureStorage.read(key: 'token');
    final body = <String, dynamic>{};

    if (shuffle != null) body['shuffle_playback'] = shuffle;
    if (order != null) body['order_playback'] = order;

    await http.patch(
      Uri.parse(
        '$server/update/custom_music_player_settings/$_playlistSerial/',
      ),
      headers: {
        'Authorization': token ?? '',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(body),
    );
  }

  Future<void> _fetchCurrentlyPlayingTrack(String? token) async {
    if (_playlistSerial == null) return;

    final response = await http.get(
      Uri.parse('$server/get/currently_playing_track_data/$_playlistSerial/'),
      headers: {'Authorization': token ?? ''},
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body)['data'];

      if (data != null) {
        _customPlaylistTrackSerial = data['custom_playlist_track_serial'];
        _trackSerial = data['track_serial'];

        final forced = await _secureStorage.read(key: 'trackStopTime');

        if (forced == '0') {
          _resumePosition = Duration.zero;
        } else {
          _resumePosition = Duration(
            seconds: (data['track_stop_time'] ?? 0).toInt(),
          );
        }

        await _secureStorage.write(
          key: 'customMusicPlaylistTrackSerial',
          value: _customPlaylistTrackSerial,
        );

        await _secureStorage.write(
          key: 'musicPlaylistTrackSerial',
          value: _trackSerial,
        );

        await _secureStorage.write(
          key: 'playOrder',
          value: data['play_order'].toString(),
        );

        setState(() {});
      }
    }
  }

  Future<void> _fetchThumbnail(String? token) async {
    if (_customPlaylistTrackSerial == null || _playlistSerial == null) return;

    final response = await http.get(
      Uri.parse(
        '$server/get/currently_streaming_track_thumbnail/'
        '$_playlistSerial/$_customPlaylistTrackSerial/',
      ),
      headers: {'Authorization': token ?? ''},
    );

    if (response.statusCode == 200) {
      setState(() {
        _thumbnailBytes = response.bodyBytes;
      });
    }
  }

  Future<void> _saveHistoryPosition() async {
    if (_isSavingHistory) return;
    if (_playlistSerial == null ||
        _customPlaylistTrackSerial == null ||
        _trackSerial == null)
      return;

    try {
      _isSavingHistory = true;

      final token = await _secureStorage.read(key: 'token');
      final seconds = _audioPlayer.position.inSeconds;

      await http.post(
        Uri.parse('$server/update/custom_music_history/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'playlist_serial': _playlistSerial,
          'custom_track_serial': _customPlaylistTrackSerial,
          'track_serial': _trackSerial,
          'track_stop_time': seconds,
        }),
      );
    } catch (_) {
    } finally {
      _isSavingHistory = false;
    }
  }

  Future<void> _startStreaming() async {
    if (_trackSerial == null || _customPlaylistTrackSerial == null) return;

    final token = await _secureStorage.read(key: 'token');
    await http.post(
      Uri.parse('$server/update/currently_playing_track/'),
      headers: {
        'Authorization': token ?? '',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'playlist_serial': _playlistSerial,
        'track_serial': _trackSerial,
        'custom_track_serial': _customPlaylistTrackSerial,
      }),
    );

    final url =
        '$server/get/currently_streaming_track_stream_data/'
        '$_trackSerial/$_customPlaylistTrackSerial/';

    await _audioPlayer.setUrl(url);

    await _audioPlayer.processingStateStream.firstWhere(
      (state) => state == ProcessingState.ready,
    );

    if (_resumePosition > Duration.zero) {
      await _audioPlayer.seek(_resumePosition);
      _currentPosition = _resumePosition;
    }

    await _audioPlayer.play();
  }

  Future<void> _nextTrack() async {
    await _saveHistoryPosition();

    final token = await _secureStorage.read(key: 'token');
    final playOrderString = await _secureStorage.read(key: 'playOrder');
    int playOrder = int.tryParse(playOrderString ?? '1') ?? 1;

    final response = await http.get(
      Uri.parse(
        '$server/get/next_track_in_custom_playlist/'
        '$_playlistSerial/$playOrder/',
      ),
      headers: {'Authorization': token ?? ''},
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body)['data'];

      _trackSerial = data['track_serial'];
      playOrder = data['play_order'];

      await _secureStorage.write(
        key: 'musicPlaylistTrackSerial',
        value: _trackSerial,
      );

      await _secureStorage.write(key: 'playOrder', value: playOrder.toString());

      await _reloadAfterTrackChange();
    }
  }

  Future<void> _previousTrack() async {
    await _saveHistoryPosition();

    final token = await _secureStorage.read(key: 'token');
    final playOrderString = await _secureStorage.read(key: 'playOrder');
    int playOrder = int.tryParse(playOrderString ?? '1') ?? 1;

    final response = await http.get(
      Uri.parse(
        '$server/get/previous_track_in_custom_playlist/'
        '$_playlistSerial/$playOrder/',
      ),
      headers: {'Authorization': token ?? ''},
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body)['data'];

      _trackSerial = data['track_serial'];
      playOrder = data['play_order'];

      await _secureStorage.write(
        key: 'musicPlaylistTrackSerial',
        value: _trackSerial,
      );

      await _secureStorage.write(key: 'playOrder', value: playOrder.toString());

      await _reloadAfterTrackChange();
    }
  }

  Future<void> _reloadAfterTrackChange() async {
    await _audioPlayer.stop();
    final token = await _secureStorage.read(key: 'token');
    await _fetchCurrentlyPlayingTrack(token);
    await _fetchThumbnail(token);
    _hasStartedStreaming = false;
    await _togglePlay();
  }

  void _listenToPlayer() {
    _positionSub = _audioPlayer.positionStream.listen((p) {
      if (!mounted) return;
      if (!_isUserSeeking) {
        setState(() => _currentPosition = p);
      }
    });

    _durationSub = _audioPlayer.durationStream.listen((d) {
      if (!mounted) return;
      setState(() => _totalDuration = d ?? Duration.zero);
    });

    _playerStateSub = _audioPlayer.playerStateStream.listen((s) {
      if (!mounted) return;
      setState(() => _isPlaying = s.playing);
    });
  }

  Future<void> _togglePlay() async {
    if (_isPlaying) {
      await _audioPlayer.pause();
      await _saveHistoryPosition();
    } else {
      if (!_hasStartedStreaming) {
        _hasStartedStreaming = true;
        await _startStreaming();
      } else {
        await _audioPlayer.play();
      }
    }
  }

  Future<void> _toggleShuffle() async {
    final newValue = !_shuffleEnabled;
    setState(() => _shuffleEnabled = newValue);
    await _updatePlayerSettings(shuffle: newValue);
  }

  Future<void> _toggleOrder() async {
    final newValue = !_orderEnabled;
    setState(() => _orderEnabled = newValue);
    await _updatePlayerSettings(order: newValue);
  }

  Future<void> _onSeek(double value) async {
    final position = Duration(milliseconds: value.toInt());
    await _audioPlayer.seek(position);
    await _saveHistoryPosition();
  }

  @override
  Widget build(BuildContext context) {
    final totalMs = _totalDuration.inMilliseconds;
    final currentMs = _currentPosition.inMilliseconds.clamp(0, totalMs);

    return IntrinsicHeight(
      child: Container(
        color: const Color(0xFF181818),
        padding: const EdgeInsets.all(12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SliderTheme(
              data: SliderTheme.of(context).copyWith(
                trackHeight: 3,
                thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
              ),
              child: Slider(
                min: 0,
                max: totalMs > 0 ? totalMs.toDouble() : 1,
                value: totalMs > 0 ? currentMs.toDouble() : 0,
                activeColor: Colors.green,
                inactiveColor: Colors.grey[800],
                onChangeStart: (_) => _isUserSeeking = true,
                onChanged: (value) {
                  setState(() {
                    _currentPosition = Duration(milliseconds: value.toInt());
                  });
                },
                onChangeEnd: (value) async {
                  _isUserSeeking = false;
                  await _onSeek(value);
                },
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Container(
                  width: 55,
                  height: 55,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                    color: Colors.grey[800],
                  ),
                  child: _thumbnailBytes != null
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.memory(
                            _thumbnailBytes!,
                            fit: BoxFit.cover,
                          ),
                        )
                      : const Icon(Icons.music_note, color: Colors.white),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      IconButton(
                        icon: Icon(
                          Icons.shuffle,
                          color: _shuffleEnabled ? Colors.green : Colors.white,
                        ),
                        onPressed: _toggleShuffle,
                      ),
                      IconButton(
                        icon: const Icon(
                          Icons.skip_previous,
                          color: Colors.white,
                        ),
                        onPressed: _previousTrack,
                      ),
                      IconButton(
                        icon: Icon(
                          _isPlaying ? Icons.pause_circle : Icons.play_circle,
                          size: 36,
                          color: Colors.white,
                        ),
                        onPressed: _togglePlay,
                      ),
                      IconButton(
                        icon: const Icon(Icons.skip_next, color: Colors.white),
                        onPressed: _nextTrack,
                      ),
                      IconButton(
                        icon: Icon(
                          Icons.repeat,
                          color: _orderEnabled ? Colors.green : Colors.white,
                        ),
                        onPressed: _toggleOrder,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
