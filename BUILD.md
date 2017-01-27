Build this roll.

On a stacki frontend with CentOS 7.x and CentOS-Updates do the following:

# git clone https://github.com/StackIQ/stacki-hdp-bridge

# cd stacki-hdp-bridge

# make

# make manifest-check

The iso should be available in:

./build-stacki-hdp-bridge-master

Add it;

# stack add pallet ./build-stacki-hdp-bridge-master/stacki-hdp-bridge-2.5-7.x.x86_64.disk1.iso

Enable it:

# stack enable pallet stacki-hdp-bridge

Follow the instructions in the README.md
