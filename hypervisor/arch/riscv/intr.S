/*
 * Copyright (C) 2023-2025 Intel Corporation.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Authors:
 *   Haicheng Li <haicheng.li@intel.com>
 */

#include <asm/trap.h>
#include <cpu.h>

	.text

	.balign 4
	.globl strap_handler
strap_handler:
	/** Save CPU registers (`struct cpu_regs` within `struct intr_excp_ctx`) to stack. */
	cpu_ctx_save

	/** Pass sp in a0, as the argument to dispatch_trap(). */
	mv	a0, sp
	call	dispatch_trap

	/** Restore CPU registers (`struct cpu_regs` within `struct intr_excp_ctx`) from stack. */
	cpu_ctx_restore
	sret
