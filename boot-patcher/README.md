# Installer

aka **kernel installer**, aka **boot-patcher**, aka **boot image patcher**

This is heavily based on [AnyKernel3](https://github.com/osm0sis/AnyKernel3).

> "[AnyKernel](https://github.com/koush/AnyKernel) is a template for an update.zip that can apply any kernel to any ROM, regardless of ramdisk." - [Koush](https://github.com/koush)
>
> [AnyKernel2](https://github.com/osm0sis/AnyKernel3/tree/6672e75f54a03276c2782f301ef5d1b77918321d) pushed the format further by allowing kernel developers to modify the underlying ramdisk for kernel feature support easily using a number of included command methods along with properties and variables to customize the installation experience to their kernel.
>
> [AnyKernel3](https://github.com/osm0sis/AnyKernel3) adds the power of [topjohnwu](https://github.com/topjohnwu)'s [magiskboot](https://topjohnwu.github.io/Magisk/tools.html) for wider format support by default, and to automatically detect and retain [Magisk](https://github.com/topjohnwu/Magisk) root by patching the new `Image.*-dtb` as Magisk would.

<!--
	AnyKernel3 first released: https://github.com/osm0sis/AnyKernel3/commit/698682123053cab9e3277c9c9df783a97b3e8958
-->

```console
$ ./build.py --installer [...]
$ ./build.py [...]
```
