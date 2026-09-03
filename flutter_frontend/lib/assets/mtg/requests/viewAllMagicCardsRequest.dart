import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:syncfusion_flutter_datagrid/datagrid.dart';
import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/assets/mtg/popups/magicCardLegalitiesPopup.dart';
import 'package:flutter_frontend/assets/mtg/popups/magicCardPricesPopup.dart';
import 'package:flutter_frontend/assets/mtg/popups/magicCardJsonDownloadPopup.dart';
import 'package:flutter_frontend/assets/mtg/popups/magicCardImagePopup.dart';

class ViewAllMagicCardsRequest extends StatefulWidget {
  const ViewAllMagicCardsRequest({Key? key}) : super(key: key);

  @override
  ViewAllMagicCardsRequestState createState() =>
      ViewAllMagicCardsRequestState();
}

class ViewAllMagicCardsRequestState extends State<ViewAllMagicCardsRequest> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  List<String> activeFields = [];
  List<String> activeFieldNames = [];
  List<Map<String, dynamic>> cardData = [];

  bool _isLoading = true;
  String? _message;

  int currentPage = 1;
  bool hasMore = false;
  bool isLoadingMore = false;

  OverlayEntry? overlayEntry;

  @override
  void initState() {
    super.initState();
    _loadPage();
  }

  Future<void> refresh() async {
    await _loadPage();
  }

  Future<void> _loadPage() async {
    setState(() {
      _isLoading = true;
      _message = null;
    });

    await _fetchViewOptions();
    await _fetchCardData(loadMore: false);

    setState(() {
      _isLoading = false;
    });
  }

  Future<void> _fetchViewOptions() async {
    try {
      final token = await _storage.read(key: 'token');

      final response = await http.get(
        Uri.parse('$server/get/magic_card_view_options/'),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final body = jsonDecode(response.body);
        final data = body['data'];

        activeFields = List<String>.from(data['active_fields']);
        activeFieldNames = List<String>.from(data['active_fields_names']);
      } else {
        _message = "Failed to load view options";
      }
    } catch (e) {
      _message = "Internal server error loading view options";
    }
  }

  Future<void> _fetchCardData({bool loadMore = false}) async {
    try {
      final token = await _storage.read(key: 'token');
      final savedSql = await _storage.read(key: 'magic_sql');
      final sqlFilter = savedSql ?? "";

      final queryParams = sqlFilter.isNotEmpty
          ? "&sql=${Uri.encodeQueryComponent(sqlFilter)}"
          : "";

      final pageToLoad = loadMore ? currentPage + 1 : 1;

      final response = await http.get(
        Uri.parse(
          '$server/get/magic_card_data/?page=$pageToLoad&limit=200$queryParams',
        ),
        headers: {
          'Authorization': token ?? '',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final body = jsonDecode(response.body);
        final data = body['data'];
        final more = body['has_more'];

        final newCards = List<Map<String, dynamic>>.from(
          data.map((e) => Map<String, dynamic>.from(e)),
        );

        setState(() {
          hasMore = more;

          if (loadMore) {
            currentPage = pageToLoad;
            cardData.addAll(newCards);
          } else {
            currentPage = 1;
            cardData = newCards;
          }
        });
      } else {
        _message = "Failed to load card data";
      }
    } catch (e) {
      _message = "Internal server error loading card data";
    }
  }

  Future<void> loadMore() async {
    if (isLoadingMore || !hasMore) return;

    setState(() {
      isLoadingMore = true;
    });

    await _fetchCardData(loadMore: true);

    setState(() {
      isLoadingMore = false;
    });
  }

  void showOverlay(BuildContext context, String text) {
    hideOverlay();

    overlayEntry = OverlayEntry(
      builder: (_) => GestureDetector(
        onTap: hideOverlay,
        child: Stack(
          children: [
            Container(color: Colors.black54),
            Center(
              child: Material(
                elevation: 12,
                borderRadius: BorderRadius.circular(12),
                child: Container(
                  width: 500,
                  height: 400,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Full Text",
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Expanded(
                        child: SingleChildScrollView(
                          child: Text(
                            text,
                            style: const TextStyle(fontSize: 15),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );

    Overlay.of(context).insert(overlayEntry!);
  }

  void hideOverlay() {
    overlayEntry?.remove();
    overlayEntry = null;
  }

  MagicCardDataSource buildDataSource() {
    return MagicCardDataSource(
      cardData,
      activeFields,
      activeFieldNames,
      showOverlay,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Magic Cards')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _message != null
          ? Center(child: Text(_message!))
          : Column(
              children: [
                Expanded(
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      return Column(
                        children: [
                          SizedBox(
                            height: constraints.maxHeight - 60,
                            child: SfDataGrid(
                              source: buildDataSource(),
                              columnWidthMode: ColumnWidthMode.none,
                              frozenColumnsCount: 1,
                              allowSwiping: false,
                              gridLinesVisibility: GridLinesVisibility.both,
                              headerGridLinesVisibility:
                                  GridLinesVisibility.both,
                              columns: [
                                for (int i = 0; i < activeFields.length; i++)
                                  GridColumn(
                                    columnName: activeFields[i],
                                    width: 180,
                                    label: Container(
                                      padding: const EdgeInsets.all(8),
                                      alignment: Alignment.centerLeft,
                                      child: Text(
                                        activeFieldNames[i],
                                        softWrap: false,
                                        overflow: TextOverflow.ellipsis,
                                        style: const TextStyle(
                                          fontSize: 13,
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    ),
                                  ),
                              ],
                            ),
                          ),

                          if (hasMore)
                            Container(
                              padding: const EdgeInsets.all(12),
                              child: ElevatedButton(
                                onPressed: isLoadingMore ? null : loadMore,
                                child: isLoadingMore
                                    ? const SizedBox(
                                        height: 20,
                                        width: 20,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                        ),
                                      )
                                    : const Text("Load More"),
                              ),
                            ),
                        ],
                      );
                    },
                  ),
                ),
              ],
            ),
    );
  }
}

class MagicCardDataSource extends DataGridSource {
  MagicCardDataSource(
    this.cards,
    this.activeFields,
    this.activeFieldNames,
    this.showOverlay,
  ) {
    buildRows();
  }

  final List<Map<String, dynamic>> cards;
  final List<String> activeFields;
  final List<String> activeFieldNames;
  final void Function(BuildContext, String) showOverlay;

  List<DataGridRow> rowsList = [];

  void buildRows() {
    rowsList = cards.map((card) {
      return DataGridRow(
        cells: activeFields.map((field) {
          dynamic value = card[field] ?? "";

          if (field == "legalities") {
            value = {
              'type': 'legalities',
              'cardId': card['card_id']?.toString() ?? '',
              'cardName': card['card_name']?.toString() ?? '',
            };
          }

          if (field == "prices") {
            value = {
              'type': 'prices',
              'cardId': card['card_id']?.toString() ?? '',
              'cardName': card['card_name']?.toString() ?? '',
            };
          }

          if (field == "json_data") {
            value = {
              'type': 'json_download',
              'cardId': card['card_id']?.toString() ?? '',
              'cardName': card['card_name']?.toString() ?? '',
            };
          }

          if (field == "card_image") {
            value = {
              'type': 'card_image',
              'cardId': card['card_id']?.toString() ?? '',
              'cardName': card['card_name']?.toString() ?? '',
            };
          }

          return DataGridCell<dynamic>(columnName: field, value: value);
        }).toList(),
      );
    }).toList();
  }

  @override
  List<DataGridRow> get rows => rowsList;

  @override
  DataGridRowAdapter buildRow(DataGridRow row) {
    return DataGridRowAdapter(
      cells: row.getCells().map((cell) {
        final rawValue = cell.value;
        final column = cell.columnName;

        final isExpandable = column == "oracle_text" || column == "flavor_text";

        final bool isLegalitiesCell =
            rawValue is Map && rawValue['type'] == 'legalities';
        final bool isPricesCell =
            rawValue is Map && rawValue['type'] == 'prices';
        final bool isJsonDownloadCell =
            rawValue is Map && rawValue['type'] == 'json_download';
        final bool isCardImageCell =
            rawValue is Map && rawValue['type'] == 'card_image';

        return Builder(
          builder: (context) {
            if (isLegalitiesCell) {
              final cardId = rawValue['cardId'];
              final cardName = rawValue['cardName'];

              return GestureDetector(
                onTap: () {
                  showDialog(
                    context: context,
                    builder: (_) => MagicCardLegalitiesPopup(
                      cardId: cardId,
                      cardName: cardName,
                    ),
                  );
                },
                child: Row(
                  children: [
                    const Icon(Icons.gavel, size: 16, color: Colors.blue),
                    const SizedBox(width: 8),
                    const Text(
                      "Show legalities",
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.blue,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ],
                ),
              );
            }

            if (isPricesCell) {
              final cardId = rawValue['cardId'];
              final cardName = rawValue['cardName'];

              return GestureDetector(
                onTap: () {
                  showDialog(
                    context: context,
                    builder: (_) => MagicCardPricesPopup(
                      cardId: cardId,
                      cardName: cardName,
                    ),
                  );
                },
                child: Row(
                  children: [
                    const Icon(
                      Icons.attach_money,
                      size: 16,
                      color: Colors.blue,
                    ),
                    const SizedBox(width: 8),
                    const Text(
                      "Show prices",
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.blue,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ],
                ),
              );
            }

            if (isJsonDownloadCell) {
              final cardId = rawValue['cardId'];
              final cardName = rawValue['cardName'];

              return GestureDetector(
                onTap: () {
                  showDialog(
                    context: context,
                    builder: (_) => MagicCardJsonDownloadPopup(
                      cardId: cardId,
                      cardName: cardName,
                    ),
                  );
                },
                child: Row(
                  children: [
                    const Icon(Icons.download, size: 16, color: Colors.blue),
                    const SizedBox(width: 8),
                    const Text(
                      "Download JSON",
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.blue,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ],
                ),
              );
            }

            if (isCardImageCell) {
              final cardId = rawValue['cardId'];
              final cardName = rawValue['cardName'];

              return GestureDetector(
                onTap: () {
                  showDialog(
                    context: context,
                    builder: (_) =>
                        MagicCardImagePopup(cardId: cardId, cardName: cardName),
                  );
                },
                child: Row(
                  children: [
                    const Icon(Icons.image, size: 16, color: Colors.blue),
                    const SizedBox(width: 8),
                    const Text(
                      "Show images",
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.blue,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ],
                ),
              );
            }

            final valueStr = rawValue?.toString() ?? "";

            return GestureDetector(
              onTap: isExpandable ? () => showOverlay(context, valueStr) : null,
              child: Text(
                valueStr.length > 40
                    ? valueStr.substring(0, 40) + "..."
                    : valueStr,
                softWrap: false,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 12,
                  color: isExpandable ? Colors.blue : Colors.black,
                ),
              ),
            );
          },
        );
      }).toList(),
    );
  }
}
