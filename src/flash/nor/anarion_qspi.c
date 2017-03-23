/*
 * Copyright (C) Adaptrum, Inc.
 * (Written by Alexandru Gagniuc <mr.nuke.me@gmail.com> for Adaptrum, Inc.)
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "imp.h"
#include "spi.h"
#include <helper/time_support.h>
#include <stdint.h>

#define ASPI_REG_CLOCK			0x00
#define ASPI_REG_GO			0x04
#define ASPI_REG_CHAIN			0x08
#define ASPI_REG_CMD1			0x0c
#define ASPI_REG_CMD2			0x10
#define ASPI_REG_ADDR1			0x14
#define ASPI_REG_ADDR2			0x18
#define ASPI_REG_PERF1			0x1c
#define ASPI_REG_PERF2			0x20
#define ASPI_REG_HI_Z			0x24
#define ASPI_REG_BYTE_COUNT		0x28
#define ASPI_REG_DATA1			0x2c
#define ASPI_REG_DATA2			0x30
#define ASPI_REG_FINISH			0x34
#define ASPI_REG_XIP			0x38
#define ASPI_REG_FIFO_STATUS		0x3c
#define ASPI_REG_LAT			0x40
#define ASPI_REG_OUT_DELAY0		0x44
#define ASPI_REG_OUT_DELAY_1		0x48
#define ASPI_REG_IN_DELAY0		0x4c
#define ASPI_REG_IN_DELAY_1		0x50
#define ASPI_REG_DQS_DELAY		0x54
#define ASPI_REG_STATUS			0x58
#define ASPI_REG_IRQ_ENABLE		0x5c
#define ASPI_REG_IRQ_STATUS		0x60
#define ASPI_REG_AXI_BAR		0x64
#define ASPI_REG_READ_CFG		0x6c

#define ASPI_DATA_LEN_MASK		0x3fff
#define ASPI_MAX_XFER_LEN		(size_t)(ASPI_DATA_LEN_MASK + 1)
#define ASPI_FIFO_SIZE			64
#define CHAIN_LEN(x)			((x - 1) & ASPI_DATA_LEN_MASK)

#define ASPI_STATUS_BUSY		(1 << 2)

#define MODE_IO_X1			(0 << 16)
#define MODE_IO_X2			(1 << 16)
#define MODE_IO_X4			(2 << 16)
#define MODE_IO_SDR_POS_SKEW		(0 << 20)
#define MODE_IO_SDR_NEG_SKEW		(1 << 20)
#define MODE_IO_DDR_34_SKEW		(2 << 20)
#define MODE_IO_DDR_PN_SKEW		(3 << 20)
#define MODE_IO_DDR_DQS			(5 << 20)

union stupid_qspi_reg {
	uint32_t reg;
	uint8_t b[sizeof(uint32_t)];
};

struct anarion_qspi_flash_bank {
	uint32_t reg_base;
	uint32_t bank_num;
	const struct flash_device *flash;
};

struct qspi_io_chain {
	uint8_t action;
	uint32_t data;
	uint16_t data_len;
	uint32_t mode;
};

enum chain_code {
	CHAIN_NOP = 0,
	CHAIN_CMD = 1,
	CHAIN_ADDR = 2,
	CHAIN_WTFIUM = 3,
	CHAIN_HI_Z = 4,
	CHAIN_DATA_OUT = 5,
	CHAIN_DATA_IN = 6,
	CHAIN_FINISH = 7,
};

static const struct chain_to_reg {
	uint8_t data_reg;
	uint8_t ctl_reg;
} chain_to_reg_map[] = {
	[CHAIN_NOP] =		{0, 0},
	[CHAIN_CMD] =		{ASPI_REG_CMD1, ASPI_REG_CMD2},
	[CHAIN_ADDR] =		{ASPI_REG_ADDR1, ASPI_REG_ADDR2},
	[CHAIN_WTFIUM] =	{0, 0},
	[CHAIN_HI_Z] =		{0, ASPI_REG_HI_Z},
	[CHAIN_DATA_OUT] =	{0, ASPI_REG_DATA2},
	[CHAIN_DATA_IN] =	{0, ASPI_REG_DATA2},
	[CHAIN_FINISH] =	{0, ASPI_REG_FINISH},
};

static uint32_t aspi_read_reg(struct flash_bank *bank, uint8_t reg)
{
	uint32_t val;
	struct anarion_qspi_flash_bank *aspi = bank->driver_priv;

	target_read_u32(bank->target, aspi->reg_base + reg, &val);
	return val;
};

static void aspi_write_reg(struct flash_bank *bank, uint8_t reg, uint32_t val)
{
	struct anarion_qspi_flash_bank *aspi = bank->driver_priv;

	target_write_u32(bank->target, aspi->reg_base + reg, val);
};

static void aspi_reset_controller(struct flash_bank *bank)
{
	aspi_write_reg(bank, ASPI_REG_CLOCK, 3);
	aspi_write_reg(bank, ASPI_REG_BYTE_COUNT, 4);
}

static void aspi_setup_chain(struct flash_bank *bank,
			     const struct qspi_io_chain *chain, size_t chain_len)
{
	size_t i;
	uint32_t chain_reg = 0;
	const struct qspi_io_chain *link;
	const struct chain_to_reg *regs;

	for (link = chain, i = 0; i < chain_len; i++, link++) {
		regs = &chain_to_reg_map[link->action];

		if (link->data_len && regs->data_reg)
			aspi_write_reg(bank, regs->data_reg, link->data);

		aspi_write_reg(bank, regs->ctl_reg, CHAIN_LEN(link->data_len) | link->mode);

		chain_reg |= link->action << (i * 4);
	}

	chain_reg |= CHAIN_FINISH << (i * 4);

	aspi_write_reg(bank, ASPI_REG_CHAIN, chain_reg);
}

static void aspi_setup_default_read_chain(struct flash_bank *bank)
{
	struct qspi_io_chain chain[] =  {
		{CHAIN_CMD, SPIFLASH_READ, 1, MODE_IO_X1},
		{CHAIN_ADDR, 0, 3, MODE_IO_X1},
		{CHAIN_DATA_IN, 0, 4, MODE_IO_X1},
	};
	aspi_setup_chain(bank, chain, ARRAY_SIZE(chain));
}

static int aspi_execute_chain(struct flash_bank *bank)
{
	int64_t start;

	aspi_write_reg(bank, ASPI_REG_GO, 1);

	start = timeval_ms();
	while (aspi_read_reg(bank, ASPI_REG_STATUS) & ASPI_STATUS_BUSY) {
		if ((timeval_ms() - start) > 1000 /*ASPI_TIMEOUT_US*/)
			return ERROR_FAIL;
	}

	return 0;
}

static int aspi_send_cmd(struct flash_bank *bank, uint8_t cmd)
{
	struct qspi_io_chain chain[] =  {
		{CHAIN_CMD, cmd, 1, MODE_IO_X1},
	};
	aspi_setup_chain(bank, chain, 1);
	return aspi_execute_chain(bank);
}

/* Send command and get back exactly 4 bytes of data. */
static int aspi_send_cmd_data_in(struct flash_bank *bank, uint8_t cmd,
				 uint32_t *data)
{
	int ret;

	struct qspi_io_chain chain[] =  {
		{CHAIN_CMD, cmd, 1, MODE_IO_X1},
		{CHAIN_DATA_IN, 0, 4, MODE_IO_X1},
	};
	aspi_setup_chain(bank, chain, 2);
	ret = aspi_execute_chain(bank);
	*data = aspi_read_reg(bank, ASPI_REG_DATA1);

	return ret;
}

static int aspi_erase_sector(struct flash_bank *bank, uint32_t addr)
{
	struct anarion_qspi_flash_bank *aspi = bank->driver_priv;

	struct qspi_io_chain chain[] =  {
		{CHAIN_CMD, aspi->flash->erase_cmd, 1, MODE_IO_X1},
		{CHAIN_ADDR, addr, 3, MODE_IO_X1},
	};
	aspi_setup_chain(bank, chain, 2);
	return aspi_execute_chain(bank);
}

static void aspi_seed_fifo(struct flash_bank *bank,
			   const uint8_t *buf, size_t len)
{
	uint32_t data;

	aspi_write_reg(bank, ASPI_REG_BYTE_COUNT, sizeof(uint32_t));
	while (len >= 4) {
		memcpy(&data, buf, sizeof(data));
		aspi_write_reg(bank, ASPI_REG_DATA1, data);
		buf += 4;
		len -= 4;
	}

	if (len) {
		aspi_write_reg(bank, ASPI_REG_BYTE_COUNT, len);
		memcpy(&data, buf, len);
		aspi_write_reg(bank, ASPI_REG_DATA1, data);
	}
}

static int aspi_write_page(struct flash_bank *bank, uint32_t addr,
			   const uint8_t *buf, size_t len)
{
	struct qspi_io_chain chain[] =  {
		{CHAIN_CMD, SPIFLASH_PAGE_PROGRAM, 1, MODE_IO_X1},
		{CHAIN_ADDR, addr, 3, MODE_IO_X1},
		{CHAIN_DATA_OUT, 0, len, MODE_IO_X1},
	};

	aspi_setup_chain(bank, chain, ARRAY_SIZE(chain));
	aspi_seed_fifo(bank, buf, len);
	return aspi_execute_chain(bank);
}

static int aspi_wait_flash_ready(struct flash_bank *bank)
{
	int ret, status;
	uint32_t data;
	int64_t start = timeval_ms();

	do {
		ret = aspi_send_cmd_data_in(bank, SPIFLASH_READ_STATUS, &data);
		if (ret != ERROR_OK)
			return ret;

		status = data & 0xff;

		if ((timeval_ms() - start > 1000))
			return ERROR_FAIL;

	} while (status & SPIFLASH_BSY_BIT);

	return ERROR_OK;
}

static int anarion_qspi_flash_erase(struct flash_bank *bank, int start, int end)
{
	int ret, sector;
	uint32_t addr, end_addr;
	struct anarion_qspi_flash_bank *aspi = bank->driver_priv;

	aspi_reset_controller(bank);

	for (sector = start; sector <= end; sector++) {
		addr = sector * aspi->flash->sectorsize;
		end_addr = addr + aspi->flash->sectorsize -1;
		LOG_INFO("Erasing sector %x -> %x", addr, end_addr);

		ret = aspi_send_cmd(bank, SPIFLASH_WRITE_ENABLE);
		if (ret != ERROR_OK)
			return ret;

		ret = aspi_erase_sector(bank, addr);
		if (ret != ERROR_OK)
			return ret;

		ret = aspi_wait_flash_ready(bank);
		if (ret != ERROR_OK)
			return ret;
	}

	aspi_setup_default_read_chain(bank);
	return ERROR_OK;
}

static int anarion_qspi_flash_write(struct flash_bank *bank, const uint8_t *buf,
				    uint32_t offset, uint32_t len)
{
	int ret;
	uint32_t addr, last_addr, step_size, xfer_len;
	struct anarion_qspi_flash_bank *aspi = bank->driver_priv;

	step_size = MIN(aspi->flash->pagesize, ASPI_FIFO_SIZE);

	last_addr = offset + len;
	for (addr = offset; addr < last_addr; addr += step_size) {
		xfer_len = MIN(step_size, len);

		ret = aspi_send_cmd(bank, SPIFLASH_WRITE_ENABLE);
		if (ret != ERROR_OK)
			return ret;

		ret = aspi_write_page(bank, addr, buf, xfer_len);
		if (ret != ERROR_OK)
			return ret;

		ret = aspi_wait_flash_ready(bank);
		if (ret != ERROR_OK)
			return ret;

		buf += xfer_len;
		len -= xfer_len;
	}

	aspi_setup_default_read_chain(bank);
	return ERROR_OK;
}

int anarion_qspi_flash_read(struct flash_bank *bank, uint8_t *buffer,
				uint32_t offset, uint32_t count)
{
	LOG_ERROR("%s: NOT IMPLEMENTED\n", __func__);
	return ERROR_FAIL;
}

static int anarion_qspi_probe(struct flash_bank *bank)
{
	int i;
	uint32_t id;
	union stupid_qspi_reg data_reg;
	const struct flash_device *flash;
	struct anarion_qspi_flash_bank *aspi = bank->driver_priv;

	/* Reset the controller */
	aspi_write_reg(bank, ASPI_REG_CLOCK, 3);

	aspi_send_cmd_data_in(bank, SPIFLASH_READ_ID, &data_reg.reg);

	/* The DATA register is 4-bytes, little endian */
	id = data_reg.b[0] << 0;
	id |= data_reg.b[1] << 8;
	id |= data_reg.b[2] << 16;
	id |= data_reg.b[3] << 24;

	for (flash = flash_devices; flash->name; flash++) {
		if (flash->device_id == id) {
			break;
		}
	}

	if (!flash->name) {
		LOG_ERROR("Unknown flash chip with id %x\n", id);
		return ERROR_FAIL;
	}

	aspi->flash = flash;
	bank->size = flash->size_in_bytes;
	bank->num_sectors = bank->size / flash->sectorsize;
	bank->sectors = malloc(sizeof(struct flash_sector) * bank->num_sectors);
	if (bank->sectors == NULL) {
		LOG_ERROR("Memory big bada fail");
		return ERROR_FAIL;
	}

	for (i = 0; i < bank->num_sectors; i++) {
		bank->sectors[i].offset = i * flash->sectorsize;
		bank->sectors[i].size = flash->sectorsize;
		bank->sectors[i].is_erased = -1;
		bank->sectors[i].is_protected = 0;
	}

	aspi_setup_default_read_chain(bank);
	return ERROR_OK;
}
static int anarion_qspi_auto_probe(struct flash_bank *bank)
{
	struct anarion_qspi_flash_bank *aspi = bank->driver_priv;
	if (aspi->flash)
		return ERROR_OK;
	return anarion_qspi_probe(bank);
}

static int anarion_qspi_flash_erase_check(struct flash_bank *bank)
{
	LOG_WARNING("%s NOT IMPLEMENTED!!!\n", __func__);
	return ERROR_OK;
}
static int anarion_qspi_protect_check(struct flash_bank *bank)
{
	LOG_WARNING("%s: NOT IMPLEMENTED\n", __func__);
	return ERROR_OK;
}

int anarion_qspi_get_info(struct flash_bank *bank, char *buf, int buf_size)
{
	struct anarion_qspi_flash_bank *aspi = bank->driver_priv;

	snprintf(buf, buf_size, "Anarion QSPI: flash \'%s\' (%x)",
		 aspi->flash->name, aspi->flash->device_id);

	return ERROR_OK;
}

FLASH_BANK_COMMAND_HANDLER(anarion_qspi_flash_bank_command)
{
	struct anarion_qspi_flash_bank *aspi;

	if (CMD_ARGC < 7)
		return ERROR_COMMAND_SYNTAX_ERROR;

	aspi = malloc(sizeof(struct anarion_qspi_flash_bank));
	if (aspi == NULL) {
		LOG_ERROR("Could not allocate memory");
		return ERROR_FAIL;
	}

	/* Get QSPI controller register map base address */
	COMMAND_PARSE_NUMBER(u32, CMD_ARGV[6], aspi->reg_base);
	bank->driver_priv = aspi;
	aspi->flash = NULL;

	return ERROR_OK;
}

struct flash_driver anarion_qspi_flash = {
	.name = "anarion_qspi",
	.flash_bank_command = anarion_qspi_flash_bank_command,
	.erase = anarion_qspi_flash_erase,
	.protect = NULL,
	.write = anarion_qspi_flash_write,
	.read = anarion_qspi_flash_read,
	.probe = anarion_qspi_probe,
	.auto_probe = anarion_qspi_auto_probe,
	.erase_check = anarion_qspi_flash_erase_check,
	.protect_check = anarion_qspi_protect_check,
	.info = anarion_qspi_get_info,
};
