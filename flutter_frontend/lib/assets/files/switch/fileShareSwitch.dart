import 'package:flutter/material.dart';

import 'package:flutter_frontend/assets/files/requests/viewAllShareFilesRequest.dart';
import 'package:flutter_frontend/assets/files/requests/viewAllShareFoldersRequest.dart';

class FileShareSwitch extends StatefulWidget {
  const FileShareSwitch({Key? key}) : super(key: key);

  @override
  State<FileShareSwitch> createState() => _FileShareSwitchState();
}

class _FileShareSwitchState extends State<FileShareSwitch> {
  bool _isFolderView = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Shared Items')),
      body: Column(
        children: [
          _buildToggleButtons(),
          const Divider(height: 1),
          Expanded(
            child: _isFolderView
                ? const ViewAllShareFoldersRequest()
                : const ViewAllShareFilesRequest(),
          ),
        ],
      ),
    );
  }

  Widget _buildToggleButtons() {
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton(
              onPressed: () => setState(() => _isFolderView = false),
              style: ElevatedButton.styleFrom(
                backgroundColor: !_isFolderView
                    ? Colors.blue
                    : Colors.grey[300],
                foregroundColor: !_isFolderView ? Colors.white : Colors.black,
              ),
              child: const Text('View Shared Files'),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: ElevatedButton(
              onPressed: () => setState(() => _isFolderView = true),
              style: ElevatedButton.styleFrom(
                backgroundColor: _isFolderView ? Colors.blue : Colors.grey[300],
                foregroundColor: _isFolderView ? Colors.white : Colors.black,
              ),
              child: const Text('View Shared Folders'),
            ),
          ),
        ],
      ),
    );
  }
}
