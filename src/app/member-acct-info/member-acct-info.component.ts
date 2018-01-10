import { Component, OnInit, Input } from '@angular/core';

import { MemberService } from '../member.service';
import { Globals } from '../globals';

@Component({
  selector: 'app-member-acct-info',
  templateUrl: './member-acct-info.component.html',
  styleUrls: ['./member-acct-info.component.css']
})
export class MemberAcctInfoComponent implements OnInit {
  
  constructor(
    public globals: Globals,
    private memberService: MemberService
  ) {}
  
  @Input() uID: string;
  
  ngOnChanges() { }
  
  ngOnInit() {
    if (this.globals.checkoutMessages === null) {
      this.memberService.getNotifs(this.uID)
        .subscribe(resp => this.globals.checkoutMessages = resp);
    }
  }

}
