# 修復雙重編碼問題
# 常見情況：UTF-8 -> 被誤解為 Windows-1252 -> 再轉為 UTF-8

function Fix-DoubleEncoding {
    param(
        [string]$filePath
    )
    
    $bytes = [System.IO.File]::ReadAllBytes($filePath)
    $content = [System.Text.Encoding]::UTF8.GetString($bytes)
    
    # 檢查是否有典型的雙重編碼模式
    # 例如：中文字符變成 ?� 或類似的模式
    if ($content -match '�') {
        Write-Output "檢測到可能雙重編碼的字符: $filePath"
        
        # 嘗試修復：假設是 UTF-8 -> Windows-1252 -> UTF-8
        $windows1252 = [System.Text.Encoding]::GetEncoding(1252)
        
        # 將當前內容視為 Windows-1252，轉回字節
        $bytesAs1252 = $windows1252.GetBytes($content)
        # 再將這些字節視為 UTF-8 解碼
        $fixedContent = [System.Text.Encoding]::UTF8.GetString($bytesAs1252)
        
        # 檢查修復後是否還有亂碼
        if ($fixedContent -notmatch '�' -and $fixedContent -match '研究') {
            Write-Output "修復成功！"
            $fixedContent | Set-Content -Path $filePath -Encoding UTF8
            return $true
        }
    }
    
    return $false
}

# 修復 blog.html
Fix-DoubleEncoding -filePath "blog.html"

# 修復 index.html  
Fix-DoubleEncoding -filePath "index.html"