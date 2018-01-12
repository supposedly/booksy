import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MgmtMediaComponent } from './mgmt-media.component';

describe('MgmtMediaComponent', () => {
  let component: MgmtMediaComponent;
  let fixture: ComponentFixture<MgmtMediaComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MgmtMediaComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MgmtMediaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
