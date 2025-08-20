#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "sim_flash.h"

#define FLASH_FILE "sim_flash.bin"
#define FLASH_SIZE 1024 // 1KB flash
#define SECTOR_SIZE 256 // 每個 sector 大小
#define FLASH_ERASED 0xFF

// 初始化 flash (全部填 0xFF)
void flash_init()
{
    FILE *fp = fopen(FLASH_FILE, "wb");
    if (!fp)
    {
        perror("flash_init fopen");
        exit(1);
    }
    unsigned char buf[FLASH_SIZE];
    memset(buf, FLASH_ERASED, sizeof(buf));
    fwrite(buf, 1, FLASH_SIZE, fp);
    fclose(fp);
}

// 讀取 flash
void flash_read(uint32_t addr, void *data, size_t len)
{
    FILE *fp = fopen(FLASH_FILE, "rb");
    if (!fp)
    {
        perror("flash_read fopen");
        exit(1);
    }
    fseek(fp, addr, SEEK_SET);
    fread(data, 1, len, fp);
    fclose(fp);
}

// 寫入 flash (只能從 1 -> 0)
void flash_write(uint32_t addr, const void *data, size_t len)
{
    FILE *fp = fopen(FLASH_FILE, "r+b");
    if (!fp)
    {
        perror("flash_write fopen");
        exit(1);
    }

    fseek(fp, addr, SEEK_SET);

    for (size_t i = 0; i < len; i++)
    {
        unsigned char old_byte, new_byte;
        fread(&old_byte, 1, 1, fp);
        new_byte = ((unsigned char *)data)[i];

        // 檢查是否違反 0->1
        if ((~old_byte) & new_byte)
        {
            printf("Error: Try to change 0->1 at addr %d\n", addr + (int)i);
            fclose(fp);
            return;
        }

        fseek(fp, addr + i, SEEK_SET);
        unsigned char merged = old_byte & new_byte;
        fwrite(&merged, 1, 1, fp);
    }

    fclose(fp);
}

// 擦除指定 sector
void flash_erase_sector(uint32_t sector)
{
    if (sector * SECTOR_SIZE >= FLASH_SIZE)
    {
        printf("Error: Sector %d out of range\n", sector);
        return;
    }

    FILE *fp = fopen(FLASH_FILE, "r+b");
    if (!fp)
    {
        perror("flash_erase_sector fopen");
        exit(1);
    }

    unsigned char buf[SECTOR_SIZE];
    memset(buf, FLASH_ERASED, sizeof(buf));

    fseek(fp, sector * SECTOR_SIZE, SEEK_SET);
    fwrite(buf, 1, SECTOR_SIZE, fp);

    fclose(fp);
    printf("Sector %d erased\n", sector);
}

// 測試
void sim_flash_test()
{
    flash_init();

    char data1[16] = "HelloFlash";
    flash_write(0, data1, strlen(data1) + 1);

    char buf[32];
    flash_read(0, buf, sizeof(buf));
    printf("Read: %s\n", buf);

    // 嘗試寫 0->1（應該報錯）
    char data2[16] = "XXXXXXXX";
    flash_write(0, data2, strlen(data2) + 1);

    // 擦除 sector 0
    flash_erase_sector(0);

    flash_read(0, buf, sizeof(buf));
    printf("After erasing, the first byte: 0x%02X\n", (unsigned char)buf[0]);

}
