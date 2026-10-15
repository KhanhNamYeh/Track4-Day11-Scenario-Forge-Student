MSSV: 2A202602741

Họ tên: Nguyễn Đăng Nam Khanh

# Lab 11 · Scenario Forge — báo cáo

Mọi số dưới đây lấy từ `evidence/` (chạy đầy đủ, không `--quick`, với `LAB11_MSSV=2A202602741`). Số nào không nằm trong `evidence/` thì có ghi chú "(chạy thêm)".

Thị trấn của bạn (`meta.json: _run.town`): **A** (`mc.json: _run.town = "A"`). Seeds: `meta.json: seeds` = mc 3629476096, search 602017237, test 2553165456.

## 1. Phát lại log có trung thực không? (bước A)

`replay.json`: n = 400 kịch bản, `dropped_human_crash_logs = 1` (người lái tự gây va chạm nên bỏ), `n_used = 399`.

| | va chạm | theo loại tiếp xúc |
|---|---|---|
| planner trên log phát lại (`replay`) | 94 | rear 85, side 9 |
| planner trong thế giới phản ứng (`reactive`) | 0 | – |

`crash_in_both = 0`: không va chạm nào của "phát lại" tồn tại trong thế giới phản ứng.

**Vì sao đa số là `rear`, và vì sao là va chạm giả:** trong log, xe bám đuôi (TG) chạy đúng quỹ đạo đã ghi từ lúc người lái thật ngồi sau vô lăng (người lái có `T = 1.1`, `b = 3.5`). Planner của ta phanh sớm hơn và êm hơn người lái (`T = 1.6`, `s0 = 2.5`), nhưng TG trong log không biết điều đó nên không phanh theo, và đâm vào đuôi xe ta (85/94 vụ). Trong thế giới phản ứng, TG chạy IDM và phản ứng với xe ta, nên không có vụ nào (0/399). Log không chứa phản ứng của người khác với hành vi khác của ta, nên va chạm đó là sản phẩm của việc phát lại.

**Một kịch bản trong `replay_only`:** phần tử đầu tiên, `scenario = 0`, `contact = "rear"`, `min_ttc_reactive = 2.37 s`. Trong thế giới phản ứng cùng kịch bản đó, TTC nhỏ nhất của xe ta chỉ 2,37 s (không va chạm); trong log phát lại, TG không giảm tốc và đâm vào xe ta lúc 16,95 s (ảnh dưới, `viewer.json: R-01`).

![R-01: planner trên log phát lại bị TG tông đuôi lúc 16,95 s](evidence/shots/ch9-replay-rear.png)

## 2. Kịch bản bất khả thi (bước B)

Các luật trong `feasible.is_feasible` (loại nếu **bất kỳ** luật nào vi phạm):

1. **Cắt làn cần bám đường quá mức:** gia tốc ngang đỉnh của cắt làn cosine 3,5 m trong `cutDur` giây là `a_lat = (π/cutDur)² · 3,5/2`; nếu `a_lat > μ·g` thì lốp không giữ được (đường khô μ = 0,8 → cần `cutDur` ≳ 1,48 s; đường ướt μ = 0,5 → ≳ 1,88 s).
2. **Phanh sau khi vào làn vượt μ·g:** `cutBrake > μ·g` (không xe nào giảm tốc mạnh hơn lực bám của lốp).
3. **Người đi bộ chạy:** `pedV > 2,5 m/s` (người băng ngang đường không chạy nhanh hơn thế).
4. **Tốc độ xe cắt làn** `cutV` phải thuộc (0, 22] m/s (xe đứng yên hay chạy quá 80 km/h không phải xe cắt làn của phố này).

`hunt.json: infeasible` (số mẫu bất khả thi trong 2 400 mẫu/cuộc săn): `bus_bypass` 3, `cut_in` 4, **`crosswalk_block` 32**, `rear_ended` 23. Cuộc săn `crosswalk_block` sinh nhiều nhất. Trong `cloud.json` cả 62 mẫu bất khả thi đều vi phạm luật số 1 (cắt làn quá gắt). Lý do CEM bị kéo về đó: cắt làn chớp nhoáng là cách "nguy hiểm" nhất (xe cắt vào khoảng trống không còn thời gian phản ứng), nên điểm nguy hiểm đẩy `cutDur` về phía nhỏ, ra ngoài giới hạn vật lý. Nếu **đếm** những kịch bản này là va chạm, ước lượng sẽ tính cả những tình huống không bao giờ xảy ra ngoài đời, nên xác suất báo ra bị thổi phồng; vì vậy `simulate` không chạy chúng và không đếm chúng.

## 3. Monte Carlo cho bạn biết gì (bước C1)

`mc.json`: `crashes` k = 6, `n` = 3 000, p̂ = 2,0·10⁻³, Wilson 95 % = [9,17·10⁻⁴; 4,36·10⁻³]. Cả 6 vụ là `bus_bypass` (`modes = {bus_bypass: 6}`). 13 kịch bản bất khả thi bị bỏ (`infeasible = 13`).

Để khoảng tin cậy hẹp còn ±20 % của p: 1,96·√(p/n) = 0,2·p ⇒ n ≈ 96/p ≈ 96/0,002 = **48 000** lần chạy (tính tay từ p̂, không có trong `evidence/`); hiện mới có 3 000, tức khoảng tin cậy hiện rộng hơn nhiều (từ ×0,46 đến ×2,2 quanh p̂).

Kiểu **chưa hề xuất hiện** trong 3 000 lần: `cut_in`, `crosswalk_block`, `rear_ended` và `other` đều có k = 0 (`mc.json: per_mode`). Con số đúng không phải 0 mà là **cận trên Wilson 95 % = 1,28·10⁻³** cho mỗi kiểu (`per_mode.<kiểu>.hi = 0.00128`).

## 4. Importance sampling, ESS và độ suy biến (bước C3)

`estimate.json`, mỗi seed dùng `final_n = 600` mẫu cho mỗi kiểu:

| seed | kiểu | p | hits | ess | top_share |
|---|---|---|---|---|---|
| 0 | bus_bypass | 9,32·10⁻³ | 43 | 139,0 | **0,889** |
| 0 | cut_in | 0 (cận trên 0,025) | 0 | 117,9 | 0 |
| 0 | crosswalk_block | 2,27·10⁻⁷ | 67 | 129,3 | 0,405 |
| 0 | rear_ended | 0 (cận trên 0,025) | 0 | 110,0 | 0 |
| 1 | bus_bypass | 6,63·10⁻⁴ | 42 | 122,1 | 0,155 |
| 1 | cut_in | 0 (cận trên 0,025) | 0 | 135,8 | 0 |
| 1 | crosswalk_block | 2,87·10⁻⁶ | 70 | 107,2 | **0,877** |
| 1 | rear_ended | 0 (cận trên 0,025) | 0 | 109,0 | 0 |
| 2 | bus_bypass | 7,94·10⁻⁴ | 25 | 127,4 | **0,662** |
| 2 | cut_in | 0 (cận trên 0,025) | 0 | 112,9 | 0 |
| 2 | crosswalk_block | 3,59·10⁻⁷ | 68 | 118,7 | 0,255 |
| 2 | rear_ended | 0 (cận trên 0,025) | 0 | 124,1 | 0 |

Tổng (`total`) theo seed: 9,32·10⁻³ [0; 2,69·10⁻²], 6,66·10⁻⁴ [2,92·10⁻⁴; 2,32·10⁻³], 7,94·10⁻⁴ [0; 3,12·10⁻³]; trung vị 7,94·10⁻⁴.

**Các seed có đồng ý không?** Không hẳn. `bus_bypass` chênh gần 14 lần (9,3·10⁻³ so với 6,6·10⁻⁴). Seed 1 và 2 nằm dưới đầu thấp của khoảng Wilson Monte Carlo (9,17·10⁻⁴) một chút, seed 0 nằm trên đầu cao (4,36·10⁻³); trung vị 7,9·10⁻⁴ cùng bậc với MC 2,0·10⁻³ nhưng thấp hơn khoảng 2,5 lần, đúng hướng "thường bị thấp" mà README cảnh báo. Với `crosswalk_block`, IS cho 10⁻⁷–10⁻⁶ còn MC không thấy vụ nào (k = 0, cận trên 1,28·10⁻³): hai kết quả không mâu thuẫn, nhưng IS dao động 12 lần giữa các seed nên không thể coi đó là con số chính xác.

**`top_share` > 0,5:** seed 0 `bus_bypass` (0,889), seed 1 `crosswalk_block` (0,877), seed 2 `bus_bypass` (0,662). Khi đó một mẫu duy nhất mang 66–89 % của ước lượng, nên con số thực chất là trọng số w = p/q của một kịch bản, không phải một tần suất; khoảng ±1,96·se ở các seed này cũng không đáng tin (seed 0 và 2 có `lo = 0`).

**Ngân sách:** `budget = 16 800` lần chạy mô phỏng (4 kiểu × (8 vòng × 300 + 3 seed × 600)). Cùng độ chính xác ±20 % cho một kiểu cỡ 7,9·10⁻⁴ bằng Monte Carlo cần ≈ 96/7,9·10⁻⁴ ≈ 1,2·10⁵ lần (tính tay), tức khoảng 7 lần ngân sách IS cho **cả 4 kiểu**. Nhưng ESS chỉ 107–139 trên 600 mẫu và `top_share` cao, nên lợi thế này chỉ đúng trên giấy; con số IS rất bất ổn.

**Phần `other`:** lấy từ Monte Carlo C1 (`estimate.json: other`: k = 0, n = 3 000, p = 0, `hi` = 1,28·10⁻³, `source = "mc.json"`). Không săn nó vì không có điểm nguy hiểm nào để CEM bám theo (nó là "không thuộc kiểu nào"); nếu bỏ ra khỏi tổng thì tổng không phủ hết tập va chạm, nên cận trên 1,28·10⁻³ được cộng vào `hi` của tổng.

## 5. Các kiểu thất bại (bước C2 + 3D)

`hunt.json: found` (số va chạm từng kiểu mà **cuộc săn của kiểu đó** tìm thấy):

| cuộc săn | found |
|---|---|
| bus_bypass | bus_bypass 148 |
| cut_in | crosswalk_block 1, bus_bypass 9 (**không có cut_in**) |
| crosswalk_block | crosswalk_block 33, bus_bypass 2 |
| rear_ended | crosswalk_block 10, bus_bypass 1 (**không có rear_ended**) |

- **bus_bypass** (`B-01`, 12,75 s): xe cắt làn C2 lách qua xe buýt đỗ trước vạch, chạy chậm (< 6 m/s, x < 112 m) vào làn của xe ta ngay lúc xe ta đang chạy tới; xe ta va đầu vào C2 (ảnh dưới: vòng đỏ "va chạm"; xe mờ là bản sửa `cutinLat = 3,0` chạy cùng kịch bản và không va chạm).
- **crosswalk_block** (`C-01`, 19,7 s, `kind = "block"`): người đi bộ bước ra từ sau xe buýt đỗ, xe ta thấy muộn, phanh gấp và dừng, nhưng thân xe nằm trên vạch qua đường, chắn lối người đi bộ.
- **cut_in, rear_ended: cuộc săn không tìm thấy.** Trong cả hai cuộc săn các vụ tìm được đều thuộc kiểu khác. Tôi tin điều đó ở mức yếu: IS cho cận trên 3/(0,2·600) = 0,025 mỗi kiểu (`upper_zero_hits`), còn Monte Carlo (n = 3 000) chỉ loại được mức trên 1,28·10⁻³. Không săn thấy không có nghĩa là không có.
- **Nếu chỉ chạy một cuộc săn chung:** `bus_bypass` là kiểu dễ nhất (cuộc săn riêng tìm 148 vụ, trong khi hai cuộc săn kia chỉ lẫn vào 1–9 vụ `bus_bypass`), nên CEM sẽ co về đó và không bao giờ khám phá `crosswalk_block`. Cuộc săn `crosswalk_block` cần tới vòng 6–8 mới thấy vụ đầu (số va chạm mỗi vòng: 0, 0, 0, 0, 0, 1, 9, 25).

![B-01: bus_bypass lúc 12,75 s; xe mờ = bản sửa](evidence/shots/ch9-bus-bypass.png)

![C-01: crosswalk_block lúc 19,7 s](evidence/shots/ch9-crosswalk-block.png)

## 6. Sửa planner (bước E + 3D)

`fix.json`. Chọn trên TRAIN (`choose_policy`): **`{cutinLat: 3.0}`**.

| | fail | fail_hi | fail_hi_seen | unseen | quãng đường (m) | phanh gấp / chuyến |
|---|---|---|---|---|---|---|
| policy gốc, TRAIN | 5,97·10⁻⁴ | 9,28·10⁻⁴ | 9,28·10⁻⁴ | – | 218,8 | 7,70 |
| bản sửa, TRAIN | 2,05·10⁻⁷ | 4,07·10⁻⁷ | 4,07·10⁻⁷ | bus_bypass | 218,5 | 7,56 |
| policy gốc, **TEST** | 1,20·10⁻³ | 3,62·10⁻³ (hợp lệ) | 2,34·10⁻³ | – | 215,6 | 8,34 |
| bản sửa, **TEST** | 2,01·10⁻⁶ | **3,88·10⁻²** (hợp lệ) | 3,56·10⁻⁶ | bus_bypass | 215,4 | 7,86 |

(TRAIN chỉ để sàng; con số báo cáo là TEST: seed mới và một cuộc săn mới nhắm vào chính policy đó.)

**Vì sao `fail_hi` của bản sửa (3,88·10⁻²) lớn hơn `fail` của policy gốc (1,20·10⁻³) dù bản sửa tốt hơn thật?** Trên TEST, `bus_bypass` có 0 hit trong n = 400 nên chỉ có cận hợp lệ 3/(0,2·400) = 3,75·10⁻² (`fix.json: chosen_test.bus_bypass.upper_zero_hits = 0.0375`), cộng cận `other` 1,28·10⁻³ và `crosswalk_block` 3,56·10⁻⁶ ra 3,88·10⁻². Với n = 400 không ngân sách nào chứng nhận được một kiểu "đã biến mất" dưới 10⁻²; cần cỡ 15 000 lần chạy. Cũng cần thành thật: `crosswalk_block` của bản sửa **tăng** (p = 2,01·10⁻⁶, so với 4,59·10⁻⁷ của policy gốc; `chosen_test.crosswalk_block.p`, `baseline_test.crosswalk_block.p`), tức một phần thất bại có thể đã dời sang kiểu khác (hai số này rất nhỏ và nhiễu, ESS 76–77, nên chưa kết luận chắc). Quãng đường gần như không đổi (215,4 so với 215,6 m, mất 0,1 %).

**Ảnh 3D có bóng mờ:** ảnh `B-01` ở câu 5 là một kịch bản bản sửa tránh được: xe đặc (policy gốc) va chạm C2 lúc 12,75 s, xe mờ (bản sửa) không va chạm (kiểm bằng `core.rollout` chạy thêm: gốc `[ego|C2 12,75 s]`, bản sửa `[]`; tương tự `B-02`).

**Núm "nghe thì an toàn hơn" nhưng làm tăng thất bại:** `T = 2,0` (giãn khoảng cách bám xe, nghe an toàn hơn). Trên TRAIN (`fix.json: table`) `fail` tăng từ 5,97·10⁻⁴ lên **1,35·10⁻²** (khoảng 22 lần; `fail_hi` = 3,12·10⁻²). Một ví dụ khác: `cautionV = 6,0` (chậm hơn gần vạch bị che) cho `fail` = 9,53·10⁻⁴, tệ hơn policy gốc. Giải thích (giả thuyết hợp lý với luật *gap acceptance*, **chưa tôi kiểm riêng**): xe cắt làn chờ một khe đủ rộng rồi mới vào; ta chừa khoảng trống lớn phía trước thì khe đó đủ rộng sớm hơn, xe hàng xóm được "mời" vào đúng lúc xe ta còn đang chạy tới và va chạm tăng. Thế giới phản ứng lại policy của ta, nên "an toàn hơn theo trực giác" không có nghĩa là "an toàn hơn trong thế giới đó". Ngược lại `cautionV = 5,0` làm `unseen = [crosswalk_block]` và quãng đường tụt còn 173,7 m (mất 21 %), nên không đạt ngưỡng 5 %.

## 7. Từ mô phỏng ra đường thật

Ba giả định ảnh hưởng nhiều nhất đến con số (ghi trong `avsim/space.py`):

1. **Khe chấp nhận của xe chuyển làn** (`cutGap`: log-chuẩn, trung vị 12 m ở thị trấn A, σ = 0,5). Toàn bộ `bus_bypass` (cả 6 vụ MC, 148 vụ của cuộc săn) hình thành từ việc xe C2 chấp nhận khe. Dữ liệu thật: quỹ đạo chuyển làn trong bộ dữ liệu giao thông tự nhiên (highD, NGSIM/US-101, INTERACTION), đo khe được chấp nhận theo tốc độ tương đối. Nếu người thật chấp nhận khe **nhỏ hơn** 12 m (táo bạo hơn), tần suất `bus_bypass` thật **cao hơn** con số của tôi; nếu lớn hơn thì thấp hơn.
2. **Tỉ lệ người đi bộ ngó qua xe buýt** (`pedLook` = 0,85). Quyết định liệu xe ta có thấy người đi bộ trước khi họ bước ra, nên chi phối `crosswalk_block`. Dữ liệu thật: video tại các điểm dừng xe buýt/vạch qua đường có xe đỗ che (ví dụ bộ PIE/JAAD gán nhãn hành vi người đi bộ, hoặc quan sát hiện trường của chính thành phố). Nếu thực tế ít người ngó hơn 85 %, `crosswalk_block` thật **cao hơn** tôi báo.
3. **Ma sát đường ướt** (`wet` = 0,20 với μ = 0,5, khô μ = 0,8). Quyết định quãng phanh và luật khả thi (`cutDur` tối thiểu 1,88 s so với 1,48 s). Dữ liệu thật: lịch sử thời tiết của thành phố (tỉ lệ giờ đi đường có mưa) và đo ma sát mặt đường (skid-resistance survey của sở giao thông). Nếu mưa nhiều hơn 20 % thời gian hoặc mặt đường kém bám hơn 0,5, mọi kiểu va chạm do phanh không kịp sẽ **tăng**.

## 8. Giới hạn

Xác suất tôi báo **không** nói gì về:

1. **Chỉ có một con phố, 24 s, một cảnh cố định.** Không có ngã tư, đèn giao thông, xe cứu thương, đường dốc hay trời tối; mọi tỉ lệ chỉ đúng có điều kiện trên đúng con phố này.
2. **Mọi người lái là IDM** (kể cả xe chuyển làn và TG) và người đi bộ theo một luật chờ khe đơn giản; người thật mất tập trung, nhìn điện thoại, bấm còi, chen lấn. Cũng chính vì thế "phát lại" và "phản ứng" khác nhau ở câu 1, và con số của tôi phụ thuộc vào việc luật IDM này đúng đến đâu.
3. **Cảm biến hoàn hảo, chỉ trừ phần bị xe buýt che; ego chỉ phanh, không đánh lái.** Không có nhiễu cảm biến, chậm trễ truyền thông, hay phanh/lái kết hợp. Vì vậy các tần suất ở câu 9 chỉ cho biết planner này có tránh được bằng phanh hay không, không nói gì về lỗi cảm biến hay khả năng đánh lái.

Nếu có thêm một tuần: (a) đo lại `cutGap` và `pedLook` bằng dữ liệu thật (câu 7) và chạy lại IS với ~15 000 lần/kiểu ở đúng vùng bản sửa, để chứng nhận được `bus_bypass` < 10⁻³; (b) thêm một cuộc săn riêng cho `cut_in` và `rear_ended` với điểm nguy hiểm tốt hơn; (c) cho ego đánh lái.

## 9. Rắc rối của bạn (bước G + chương 10)

- **Rắc rối:** một **người đi bộ băng ngang giữa đoạn đường không có vạch** (`hazard.json`: 1 rắc rối H0, `type = "ped"`, `side = "S"`). Trong cảnh gốc tôi dựng: `x = 131,08 m`, `v = 1,868 m/s`, `trig = 31,16 m` (người bước ra khi xe ta còn cách ~31 m). Ngoài đời: người băng đường tự do (jaywalking) gần điểm dừng xe buýt, chẳng hạn người chạy qua đường để kịp lên xe. Cảnh này đã được kiểm: `mine.json: exact.planner = [ego, H0, 17.45 s]`, tức planner va chạm người đi bộ lúc 17,45 s. (Tôi dựng file bằng script từ một mẫu va chạm trong quét, không phải bằng cách chỉnh tay trong chương 10 nên chưa thử "Bạn" tự lái; xem mục dưới.)
- **Căn cứ:** planner chỉ có logic dự đoán người đi bộ (`pedBuffer`, chế độ nhường) dành cho P1 ở **vạch qua đường** (`avsim/core.py`, đoạn xử lý `P1`, các dòng 492–499). Một người bước ra ở chỗ không có vạch chỉ là một vật thể bình thường: xe ta chỉ phản ứng qua IDM khi họ đã nằm trong hành lang `cutinLat` của xe, tức là rất muộn.
- **Giả định:** `space` = `h0_x` [110; 300] m, `h0_v` [0,9; 2,0] m/s, `h0_trig` [12; 35] m; `exposure = 0,02` mỗi chuyến (`hazard.json: why` có giải thích). `h0_v`: 0,9 là đi chậm, 1,2–1,5 là bình thường, 2,0 là đi nhanh (dưới ngưỡng chạy 2,5 m/s); `h0_trig`: người thật chấp nhận khe 2–3 s, ở 12,5 m/s là 25–37 m, nên 12 m rất gắt và 35 m thoải mái; `h0_x`: toàn bộ đoạn sau xe buýt đỗ trước vạch. **`exposure = 0,02` là giả định bậc độ lớn (khoảng 1 chuyến trong 50), chưa có dữ liệu đo thật**, cần thay bằng tần suất từ dữ liệu dashcam. `exposure` được chọn **trước** khi chạy `mine`. Với `space`, tôi đã thử thêm 3 khoảng (chạy thêm, ngoài `evidence/`, n = 1 500 mỗi khoảng, cho 3–24 vụ `avoidable`) và giữ khoảng ở giữa, vì mọi khoảng đều nằm trong phạm vi có căn cứ ở trên; không chọn con số để làm rắc rối trông nguy hiểm hơn.
- **Kết quả**, theo `mine.json` (n = 1 489 phiên bản khả thi trong 1 500, `accepted` = 0,9927):

| | va chạm | avoidable | unavoidable | unattributed | low_speed | avoidable_foreknown |
|---|---|---|---|---|---|---|
| policy gốc (`baseline`) | 9 | 9 | 0 | 0 | 0 | 9 |
| bản sửa `cutinLat = 3,0` (`chosen`) | 9 | 9 | 0 | 0 | 0 | 9 |

  - P(lỗi planner | rắc rối) = 9/1 489 = **6,04·10⁻³**, Wilson 95 % [3,18·10⁻³; 1,14·10⁻²] (cả hai policy).
  - Nhân `exposure`: `per_trip` = **1,21·10⁻⁴** mỗi chuyến, cận trên `per_trip_hi` = 2,29·10⁻⁴.
  - So với `bus_bypass`: MC (`mc.json`) p̂ = 2,0·10⁻³ mỗi lần chạy, trung vị IS (`estimate.json`) 7,9·10⁻⁴. Với `exposure = 0,02`, rắc rối của tôi (1,21·10⁻⁴) thấp hơn lách xe buýt khoảng 6–16 lần. Nó **không** nguy hiểm hơn lách xe buýt, nhưng cũng không đáng bỏ qua, và vì `exposure` là giả định nên tỉ lệ này chỉ mang tính bậc độ lớn.
  - **Phân biệt ba loại:** cả 9 vụ là `avoidable` (phanh hết cỡ ngay khi thấy, cùng planner, thì không va chạm), 0 `unavoidable` (không có vụ nào mà ai phanh cũng không tránh được), 0 `unattributed` (không có va chạm thường của thị trấn lẫn vào). `avoidable` là chuẩn **lạc quan**: người phanh biết rắc rối ngay khi thấy và phanh tối đa nên nó **đếm nhiều hơn** số vụ một planner thật tránh được (đây là cận trên lỗi của planner); còn vì chỉ thử phanh (không đánh lái) nó cũng **đếm ít đi** các vụ lẽ ra đánh lái tránh được. `avoidable_foreknown = avoidable = 9`: ở rắc rối này che tầm nhìn không đóng vai trò gì.
- **Hình:** `evidence/shots/ch9-my-hazard-ped.png` (`GB-01`: người băng ngang đường va chạm lúc 18,9 s, bảng bên trái ghi "va chạm người băng ngang 18,9 s"); `GC-01` (bản sửa) cho cùng kết quả.

![GB-01: rắc rối của tôi, policy gốc, lúc 18,9 s](evidence/shots/ch9-my-hazard-ped.png)

- **Bạn tự lái thì sao:** **chưa thử.** Tôi không lái trong chương 10 (không có `ego: "script"` trong `hazard.json`), nên không có số liệu để so với planner; không bịa kết quả.
- **Cách sửa:** **không núm nào trong 12 ứng viên sửa được** (bản sửa `cutinLat = 3,0` vẫn 9/9 va chạm như policy gốc; `cutinLat` chỉ đổi hành lang phía trước cho xe lấn làn, không liên quan tới người đi bộ). Planner cần **logic mới**: dự đoán đường đi của **mọi** người đi bộ (không chỉ P1 ở vạch), tính thời gian tới điểm giao cắt với làn của xe ta (giống cách đã làm cho P1: `t_enter` so với `t_arrive + pedBuffer`) và giảm tốc ngay khi có người ở lề hoặc đang di chuyển hướng vào làn, kể cả khi không có vạch; kèm một ngưỡng "người đang ở lề, ngoài vạch, trong tầm 30–40 m" để chuyển sang chế độ thận trọng.
