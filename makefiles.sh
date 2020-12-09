# Test file for demessifier, will make a mess



for i in $(seq 1 150); do
	touch "slurm-$(($RANDOM % 1000000)).out"
        touch "core.$(($RANDOM % 1000000))"
 done
